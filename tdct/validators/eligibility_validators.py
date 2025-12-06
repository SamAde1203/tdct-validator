# tdct/validators/eligibility_validators.py

from typing import List
from .base import BaseValidator, Protocol, Finding


class AgeRangeConsistencyValidator(BaseValidator):
    """
    ELG-001:
    Ensures age_min / age_max are consistent and non-contradictory.
    """

    category = "Eligibility & Inclusion Criteria"
    code_prefix = "ELG-AGE"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        pop = protocol.get("population", {})
        age_min = pop.get("age_min")
        age_max = pop.get("age_max")

        if age_min is not None and age_max is not None and age_min >= age_max:
            findings.append(
                self.major(
                    "001",
                    "Age inclusion criteria are contradictory (age_min ≥ age_max).",
                    "Correct age range so that minimum age is strictly lower than maximum age.",
                    "Screening failures and potential regulatory rejection due to illogical eligibility criteria.",
                    context={"age_min": age_min, "age_max": age_max},
                )
            )
        return findings


class TreatmentNaiveDefinitionValidator(BaseValidator):
    """
    ELG-002:
    Checks that 'treatment-naive' is clearly defined when referenced.
    """

    category = "Eligibility & Inclusion Criteria"
    code_prefix = "ELG-NAIVE"

    def should_run(self, protocol: Protocol) -> bool:
        return "treatment_naive" in protocol.get("population", {})

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        pop = protocol.get("population", {})
        naive_def = pop.get("treatment_naive_definition")
        if not naive_def:
            findings.append(
                self.major(
                    "001",
                    "Population marked as 'treatment-naive' without an explicit operational definition.",
                    "Define treatment-naive clearly (e.g. 'no prior pharmacological therapy for the index condition, or discontinued ≥3 months with washout confirmed').",
                    "Heterogeneous population and interpretability issues for efficacy and safety signals.",
                )
            )
        return findings


class ComorbidityLogicValidator(BaseValidator):
    """
    ELG-003:
    Ensures comorbidity-related eligibility does not create logical impossibilities,
    e.g. excluding creatinine > X but requiring a GFR band that implies higher creatinine.
    """

    category = "Eligibility & Inclusion Criteria"
    code_prefix = "ELG-COMORB"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        elig = protocol.get("eligibility", {})
        gfr_band = elig.get("gfr_band")  # e.g. {"min": 30, "max": 50}
        creatinine_cutoff = elig.get("creatinine_max_mg_dl")

        if gfr_band and creatinine_cutoff:
            # Simple heuristic: if they are targeting moderate CKD but
            # use a very low creatinine ceiling, likely to exclude target population.
            if gfr_band["min"] <= 50 and creatinine_cutoff <= 1.5:
                findings.append(
                    self.major(
                        "001",
                        "GFR-based dosing band is incompatible with creatinine exclusion threshold.",
                        "Reconcile creatinine cut-off with intended GFR band or adjust dosing strategy.",
                        "Under-representation or exclusion of intended CKD subgroup; protocol dosing rules underutilised.",
                        context={"gfr_band": gfr_band, "creatinine_max": creatinine_cutoff},
                    )
                )
        return findings


class HouseholdExclusionBiasValidator(BaseValidator):
    """
    ELG-004:
    Flags potential bias if same-household exclusion is used without justification.
    """

    category = "Eligibility & Inclusion Criteria"
    code_prefix = "ELG-HH"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        elig = protocol.get("eligibility", {})
        exclusions = set(elig.get("exclusions", []))

        if "same_household_randomised" in exclusions:
            findings.append(
                self.major(
                    "001",
                    "Exclusion of participants from the same household as an already randomised participant.",
                    "Provide explicit justification for same-household exclusion or remove it to avoid selection bias.",
                    "Potential selection bias and reduced recruitment efficiency, especially in elderly or married populations.",
                )
            )
        return findings


class OverlyRestrictiveGeneralizabilityValidator(BaseValidator):
    """
    ELG-005:
    Detects obviously over-restrictive exclusions that may harm external validity.
    """

    category = "Eligibility & Inclusion Criteria"
    code_prefix = "ELG-GEN"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        elig = protocol.get("eligibility", {})
        exclusions = set(elig.get("exclusions", []))

        # Example: excluding all CKD stage 3a in a common condition trial.
        if "ckd_stage_3a" in exclusions and protocol.get("indication", "").lower() in {
            "hypertension",
            "type 2 diabetes",
            "cardiovascular disease",
        }:
            findings.append(
                self.minor(
                    "001",
                    "Exclusion of CKD stage 3a may unnecessarily limit generalisability.",
                    "Consider allowing CKD stage 3a with appropriate safety monitoring or document rationale clearly.",
                    "Reduced external validity to real-world populations where CKD stage 3a is common.",
                    context={"exclusion": "ckd_stage_3a"},
                )
            )
        return findings


class ElderlyUpperAgeJustificationValidator(BaseValidator):
    """
    ELG-006:
    Ensures high upper age limits are justified in high-risk intensive interventions.
    """

    category = "Eligibility & Inclusion Criteria"
    code_prefix = "ELG-ELD"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        pop = protocol.get("population", {})
        age_max = pop.get("age_max")
        intervention = protocol.get("intervention", {})
        intensive = bool(intervention.get("intensive_target"))

        if age_max and age_max >= 80 and intensive:
            if not protocol.get("rationale", {}).get("elderly_inclusion"):
                findings.append(
                    self.major(
                        "001",
                        "Very high upper age limit (≥80 years) in an intensive intervention trial without explicit justification.",
                        "Provide clear justification and safety mitigation strategies for including very elderly participants.",
                        "Increased risk of adverse events and regulatory or IRB concerns about risk–benefit balance.",
                        context={"age_max": age_max},
                    )
                )

        return findings
