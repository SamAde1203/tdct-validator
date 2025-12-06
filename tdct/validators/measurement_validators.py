# tdct/validators/measurement_validators.py

from typing import List
from .base import BaseValidator, Protocol, Finding


class BPMeasurementStandardisationValidator(BaseValidator):
    """
    MEA-001:
    Ensures blood pressure measurement method is explicitly defined
    when BP targets are central to the trial.
    """

    category = "Measurement & Standardisation"
    code_prefix = "MEA-BP"

    def should_run(self, protocol: Protocol) -> bool:
        endpoints = protocol.get("endpoints", {})
        all_eps = [e.lower() for e in endpoints.get("all", [])]
        return any("blood pressure" in e or "bp" in e for e in all_eps)

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        measurement = protocol.get("measurement", {})
        bp = measurement.get("bp", {})

        method = bp.get("method")
        unattended = bp.get("unattended")
        rest_minutes = bp.get("rest_minutes")

        if not method:
            findings.append(
                self.critical(
                    "001",
                    "Blood pressure measurement method is not explicitly defined despite BP being a primary outcome.",
                    "Specify exact BP measurement protocol (device type, attended vs unattended, rest period, number of readings).",
                    "Protocol–practice mismatch and risk of implementation crisis similar to SPRINT.",
                )
            )
        else:
            if "automated" in method.lower() and unattended is None:
                findings.append(
                    self.major(
                        "002",
                        "Automated BP measurement method defined without clarifying attended vs unattended conditions.",
                        "Clarify whether BP measurements are attended or unattended and standardise across sites.",
                        "Clinical translation issues due to systematic BP differences between attended and unattended methods.",
                    )
                )
            if rest_minutes is not None and rest_minutes < 5:
                findings.append(
                    self.minor(
                        "003",
                        f"BP rest period is set to {rest_minutes} minutes, shorter than typical 5-minute rest.",
                        "Increase rest period to at least 5 minutes or justify shorter duration in the protocol.",
                        "Potential overestimation of BP due to inadequate rest period.",
                        context={"rest_minutes": rest_minutes},
                    )
                )
        return findings


class LifestyleInterventionStandardisationValidator(BaseValidator):
    """
    MEA-002:
    Checks that referenced lifestyle manuals / appendices actually exist.
    """

    category = "Measurement & Standardisation"
    code_prefix = "MEA-LIFE"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        lifestyle = protocol.get("lifestyle", {})
        referenced_manual = lifestyle.get("manual_reference")
        available_appendices = set(protocol.get("appendices", []))

        if referenced_manual and referenced_manual not in available_appendices:
            findings.append(
                self.major(
                    "001",
                    f"Lifestyle manual '{referenced_manual}' is referenced but not present in appendices.",
                    "Provide the referenced lifestyle intervention manual or remove the reference.",
                    "Site-to-site variability in lifestyle advice and confounding of drug efficacy signals.",
                    context={"referenced_manual": referenced_manual, "appendices": list(available_appendices)},
                )
            )
        return findings


class BiomarkerAssaySpecificationValidator(BaseValidator):
    """
    MEA-003:
    Ensures key biomarker endpoints have assay specifications defined.
    """

    category = "Measurement & Standardisation"
    code_prefix = "MEA-BIOM"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        measurement = protocol.get("measurement", {})
        biomarkers = measurement.get("biomarkers", [])

        for biom in biomarkers:
            if not biom.get("assay_method") or not biom.get("laboratory_standard"):
                findings.append(
                    self.major(
                        "001",
                        f"Biomarker '{biom.get('name')}' lacks a fully specified assay method or laboratory standard.",
                        "Define assay method, units, and reference laboratory / certification for each key biomarker endpoint.",
                        "Measurement variability and interpretability issues across sites and over time.",
                        context={"biomarker": biom},
                    )
                )
        return findings
