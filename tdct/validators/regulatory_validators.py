# tdct/validators/regulatory_validators.py

from typing import List
from .base import BaseValidator, Protocol, Finding


class PhaseDesignationValidator(BaseValidator):
    """
    REG-001:
    Ensures declared trial phase matches design characteristics.
    """

    category = "Regulatory & Design Classification"
    code_prefix = "REG-PHASE"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        reg = protocol.get("regulatory", {})
        declared_phase = reg.get("declared_phase")
        inferred_phase = reg.get("inferred_phase")  # Pre-computed or manually tagged

        if declared_phase and inferred_phase and declared_phase != inferred_phase:
            findings.append(
                self.major(
                    "001",
                    f"Declared phase '{declared_phase}' does not match inferred design characteristics '{inferred_phase}'.",
                    "Align phase designation with ICH guidance based on sample size, objectives, and dosing strategy.",
                    "Regulatory confusion and potential delays in review due to misclassified phase.",
                    context={"declared_phase": declared_phase, "inferred_phase": inferred_phase},
                )
            )
        return findings


class ConsentSubstudyHierarchyValidator(BaseValidator):
    """
    REG-002:
    Checks that optional substudies (e.g. imaging, cognitive) have
    clearly separated consent flows and inclusion logic.
    """

    category = "Regulatory & Design Classification"
    code_prefix = "REG-CONSENT"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        substudy = protocol.get("substudies", {})
        for name, cfg in substudy.items():
            if cfg.get("requires_additional_consent") and not cfg.get("consent_process_defined"):
                findings.append(
                    self.major(
                        "001",
                        f"Substudy '{name}' requires additional consent but the consent process is not defined.",
                        "Specify timing, content, and documentation for substudy consent separate from main trial consent.",
                        "Ethical and regulatory concerns about informed consent adequacy for optional substudies.",
                        context={"substudy": name},
                    )
                )
        return findings
