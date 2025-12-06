# tdct/validators/safety_validators.py

from typing import List
from .base import BaseValidator, Protocol, Finding


class HypoglycemiaRiskValidator(BaseValidator):
    """
    SAF-001:
    Checks that elderly populations on glucose-lowering interventions
    have adequate hypoglycaemia risk exclusion.
    """

    category = "Safety & Risk Stratification"
    code_prefix = "SAF-HYPO"

    def should_run(self, protocol: Protocol) -> bool:
        pop = protocol.get("population", {})
        intervention = protocol.get("intervention", {})
        return bool(
            intervention.get("glucose_lowering")
            and pop.get("age_max", 0) >= 65
        )

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        elig = protocol.get("eligibility", {})
        exclusions = set(elig.get("exclusions", []))

        # Very simple schema assumption – adjust to your real YAML keys.
        has_12m = "severe_hypoglycemia_12m" in exclusions
        has_24m = "severe_hypoglycemia_24m" in exclusions

        if has_12m and not has_24m:
            findings.append(
                self.critical(
                    "001",
                    "Hypoglycaemia exclusion window is limited to 12 months in an elderly, glucose-lowering intensive trial.",
                    "Extend exclusion to at least 24 months OR lower maximum age threshold OR add continuous glucose monitoring requirements.",
                    "Elevated risk of severe hypoglycaemia and mortality in elderly participants.",
                    context={"current_exclusions": list(exclusions)},
                )
            )
        elif not has_12m and not has_24m:
            findings.append(
                self.critical(
                    "002",
                    "No explicit exclusion for prior severe hypoglycaemia in an elderly, glucose-lowering intensive trial.",
                    "Add exclusion for severe hypoglycaemia (requiring third-party assistance) within the past 24 months.",
                    "High likelihood of hypoglycaemia-related serious adverse events and potential trial termination.",
                    context={"current_exclusions": list(exclusions)},
                )
            )

        return findings


class FirstInHumanDoseEscalationValidator(BaseValidator):
    """
    SAF-002:
    Ensures first-in-human trials implement titration / sentinel cohort
    when doses approach or exceed HED of preclinical toxicity thresholds.
    """

    category = "Safety & Risk Stratification"
    code_prefix = "SAF-FIH"

    def should_run(self, protocol: Protocol) -> bool:
        intervention = protocol.get("intervention", {})
        return bool(intervention.get("is_first_in_human"))

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        intervention = protocol.get("intervention", {})
        doses = intervention.get("doses_mg", [])
        hed_toxicity = intervention.get("hed_toxicity_threshold_mg", None)

        # No titration config? (You can extend this to your real schema)
        titration = intervention.get("titration_schedule")
        has_titration = titration is not None

        if hed_toxicity is None or not doses:
            return findings  # nothing to compare, silently ignore

        max_dose = max(doses)

        if max_dose >= hed_toxicity and not has_titration:
            findings.append(
                self.critical(
                    "001",
                    "First-in-human trial assigns participants directly to doses at or above preclinical toxicity threshold.",
                    "Introduce dose titration (e.g. all participants start at lowest dose) or sentinel cohorts prior to full-dose exposure.",
                    "Increased risk of early serious adverse events and DSMB-driven protocol suspension.",
                    context={"max_dose_mg": max_dose, "hed_toxicity_mg": hed_toxicity},
                )
            )

        return findings


class AEExclusionCoverageValidator(BaseValidator):
    """
    SAF-003:
    Checks for presence of core safety exclusions for the relevant indication,
    e.g. recent MI/stroke in high-risk cardiometabolic trials.
    """

    category = "Safety & Risk Stratification"
    code_prefix = "SAF-AE"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        indication = protocol.get("indication", "").lower()
        elig = protocol.get("eligibility", {})
        exclusions = set(elig.get("exclusions", []))

        # Example for cardiometabolic context
        if "diabetes" in indication or "hypertension" in indication:
            critical_exclusions = {
                "recent_mi_6m",
                "recent_stroke_6m",
                "unstable_angina",
            }
            missing = critical_exclusions.difference(exclusions)
            if missing:
                findings.append(
                    self.major(
                        "001",
                        "Core cardiovascular safety exclusions are missing for a high-risk cardiometabolic trial.",
                        "Add exclusions for recent MI, stroke, or unstable angina according to guideline-based safety thresholds.",
                        "Increased risk of preventable serious cardiovascular events during the trial.",
                        context={"missing_exclusions": list(missing)},
                    )
                )

        return findings


class DDIDrugInteractionValidator(BaseValidator):
    """
    SAF-004:
    Basic check that known severe drug–drug interactions are at least
    acknowledged / excluded when a trial uses high-risk mechanisms.
    """

    category = "Safety & Risk Stratification"
    code_prefix = "SAF-DDI"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        intervention = protocol.get("intervention", {})
        mech = intervention.get("mechanism", "").lower()
        elig = protocol.get("eligibility", {})
        exclusions = set(elig.get("exclusions", []))

        # Simple illustrative rule for strong CYP3A4 interactions.
        if "cyp3a4" in mech:
            if "strong_cyp3a4_inhibitors" not in exclusions:
                findings.append(
                    self.major(
                        "001",
                        "Trial uses a CYP3A4-metabolised agent without excluding strong CYP3A4 inhibitors.",
                        "Add exclusion criterion for strong CYP3A4 inhibitors (per FDA guidance list) or mandate dose adjustments.",
                        "Elevated risk of supratherapeutic exposure and toxicity due to drug–drug interactions.",
                        context={"mechanism": mech},
                    )
                )

        return findings
