"""
TDCT Runner

- Loads a protocol YAML
- Runs all registered validators
- Aggregates findings
- Writes JSON output to `findings/<trial_id>_findings.json`
"""

from __future__ import annotations

import argparse
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Protocol

from .utils import (
    compute_severity_counts,
    get_trial_id,
    info,
    load_protocol,
    save_json,
)


class Validator(Protocol):
    """
    Minimal protocol for TDCT validators.

    A validator can optionally implement a `trigger` method
    and must implement `validate(protocol) -> list[dict]` OR a single dict.
    """

    id: str  # e.g. "SAF-001"

    def validate(self, protocol: Dict[str, Any]) -> Any:
        ...


def _discover_validators() -> List[Validator]:
    """
    Discover validators from `tdct.validators`.

    Expected patterns:
    - A module `tdct.validators` exposing `VALIDATORS = [Validator, ...]`
    OR
    - A function `get_validators()` returning a list of validator instances.

    Returns
    -------
    list
        List of validator instances. Empty list if none found.
    """
    try:
        module = import_module("tdct.validators")
    except ModuleNotFoundError:
        info("No tdct.validators module found – running with zero validators.")
        return []

    validators: List[Validator] = []

    if hasattr(module, "get_validators"):
        validators = list(module.get_validators())  # type: ignore[attr-defined]
        info(f"Loaded {len(validators)} validators via get_validators().")
        return validators

    if hasattr(module, "VALIDATORS"):
        validators = list(module.VALIDATORS)  # type: ignore[attr-defined]
        info(f"Loaded {len(validators)} validators from VALIDATORS.")
        return validators

    info("tdct.validators found, but no VALIDATORS or get_validators() defined.")
    return []


class TDCTRunner:
    """
    Main entry point for executing TDCT protocol validation.
    """

    def __init__(self, validators: List[Validator] | None = None) -> None:
        if validators is None:
            validators = _discover_validators()
        self.validators: List[Validator] = validators

    def run(self, protocol: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all validators on a single protocol.

        Parameters
        ----------
        protocol : dict

        Returns
        -------
        dict
            TDCT result payload:
            {
              "trial_id": ...,
              "total_findings": int,
              "severity_counts": {...},
              "findings": [...]
            }
        """
        trial_id = get_trial_id(protocol)
        info(f"Running TDCT on trial: {trial_id}")
        all_findings: List[Dict[str, Any]] = []

        for v in self.validators:
            v_name = getattr(v, "id", v.__class__.__name__)
            info(f"  -> Validator: {v_name}")
            try:
                result = v.validate(protocol)
            except Exception as exc:  # noqa: BLE001 - explicit, local catch
                info(f"    !! Validator {v_name} raised an exception: {exc}")
                continue

            if result is None:
                continue

            if isinstance(result, list):
                for f in result:
                    if f:
                        all_findings.append(self._normalise_finding(f, v))
            elif isinstance(result, dict):
                all_findings.append(self._normalise_finding(result, v))
            else:
                info(f"    !! Validator {v_name} returned unsupported type: {type(result)}")

        severity_counts = compute_severity_counts(all_findings)
        total = len(all_findings)

        info(f"Completed. Total findings: {total}")

        return {
            "trial_id": trial_id,
            "total_findings": total,
            "severity_counts": severity_counts,
            "findings": all_findings,
        }

    @staticmethod
    def _normalise_finding(finding: Dict[str, Any], validator: Validator) -> Dict[str, Any]:
        """
        Ensure each finding has minimal standard fields.

        Adds `validator_id` if not already present.
        """
        out = dict(finding)  # shallow copy
        if "validator_id" not in out:
            out["validator_id"] = getattr(validator, "id", validator.__class__.__name__)
        # Normalise severity to uppercase if present
        if "severity" in out and isinstance(out["severity"], str):
            out["severity"] = out["severity"].upper()
        return out


def run_tdct(protocol_path: str | Path, output_path: str | Path | None = None) -> Path:
    """
    Convenience function – load protocol, run TDCT, write JSON.

    Parameters
    ----------
    protocol_path : str or Path
        Path to YAML protocol file.
    output_path : str or Path, optional
        Output JSON path. If None, defaults to:
        `findings/<trial_id>_findings.json`

    Returns
    -------
    Path
        Path to the written JSON file.
    """
    protocol = load_protocol(protocol_path)
    runner = TDCTRunner()
    result = runner.run(protocol)

    trial_id = result.get("trial_id", "UNKNOWN_TRIAL")
    if output_path is None:
        output_path = Path("findings") / f"{trial_id.lower()}_findings.json"

    output_path = Path(output_path)
    save_json(result, output_path)
    info(f"Results written to: {output_path}")
    return output_path


def main() -> None:
    """
    CLI entry point.

    Example:
        python -m tdct.runner --protocol protocols/hunter_protocol.yaml
    """
    parser = argparse.ArgumentParser(
        description="TDCT – Trial Design Consistency Testing"
    )
    parser.add_argument(
        "--protocol",
        required=True,
        help="Path to protocol YAML file.",
    )
    parser.add_argument(
        "--out",
        required=False,
        help="Optional path to output JSON. Defaults to findings/<trial_id>_findings.json",
    )

    args = parser.parse_args()
    protocol_path = args.protocol
    output_path = args.out

    run_tdct(protocol_path, output_path)


if __name__ == "__main__":
    main()
