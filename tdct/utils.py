"""
Utility helpers for TDCT:
- File I/O (YAML / JSON)
- Severity aggregation
- Simple logging helpers
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_protocol(path: str | Path) -> Dict[str, Any]:
    """
    Load a trial protocol from a YAML file.

    Parameters
    ----------
    path : str or Path
        Path to the protocol YAML file.

    Returns
    -------
    dict
        Parsed protocol as a Python dictionary.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Protocol file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Protocol YAML must define a mapping at the top level: {path}")

    return data


def save_json(obj: Any, path: str | Path) -> None:
    """
    Save an object as pretty-printed JSON.

    Parameters
    ----------
    obj : Any
        The object to serialise.
    path : str or Path
        Output path for the JSON file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def compute_severity_counts(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Compute severity counts from a list of findings.

    Each finding is expected to have a 'severity' key
    with values such as 'CRITICAL', 'MAJOR', 'MINOR'.

    Parameters
    ----------
    findings : list of dict

    Returns
    -------
    dict
        Mapping of severity -> count.
    """
    counts: Dict[str, int] = {}
    for f in findings:
        severity = str(f.get("severity", "")).upper()
        if not severity:
            continue
        counts[severity] = counts.get(severity, 0) + 1
    return counts


def get_trial_id(protocol: Dict[str, Any]) -> str:
    """
    Extract trial_id from the protocol metadata.

    Falls back to 'UNKNOWN_TRIAL' if not present.

    Parameters
    ----------
    protocol : dict

    Returns
    -------
    str
    """
    meta = protocol.get("meta", {}) or {}
    trial_id = meta.get("trial_id") or meta.get("acronym") or "UNKNOWN_TRIAL"
    return str(trial_id)


def info(msg: str) -> None:
    """Simple console logger for TDCT."""
    print(f"[TDCT] {msg}")
