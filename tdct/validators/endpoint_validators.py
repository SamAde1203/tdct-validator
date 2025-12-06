# tdct/validators/endpoint_validators.py

from typing import List
from .base import BaseValidator, Protocol, Finding


class PrimaryEndpointPowerAlignmentValidator(BaseValidator):
    """
    END-001:
    Checks that declared primary endpoint aligns with power calculation.
    """

    category = "Endpoint & Statistical Design"
    code_prefix = "END-PRIM"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        endpoints = protocol.get("endpoints", {})
        stats = protocol.get("statistics", {})

        primary = endpoints.get("primary")
        powered_for = stats.get("powered_for")

        if primary and powered_for and primary != powered_for:
            findings.append(
                self.major(
                    "001",
                    f"Primary endpoint '{primary}' does not match the endpoint used in power calculation ('{powered_for}').",
                    "Align the declared primary endpoint with the powered endpoint or revise the power calculation.",
                    "Ambiguity about which endpoint the trial is truly powered to detect; interpretability and regulatory concerns.",
                    context={"primary": primary, "powered_for": powered_for},
                )
            )

        # Handle case where protocol claims 'not powered for efficacy' but labels efficacy endpoint primary
        if primary and stats.get("powered_for") is None and "efficacy" in primary.lower():
            if stats.get("claims_not_powered_for_efficacy"):
                findings.append(
                    self.major(
                        "002",
                        "Protocol labels an efficacy endpoint as primary while also stating the trial is not powered for efficacy.",
                        "Relabel the efficacy measure as exploratory or secondary, with safety as the sole primary endpoint.",
                        "Misleading interpretation of efficacy results and potential reviewer objections.",
                    )
                )
        return findings


class HbA1cTimingValidator(BaseValidator):
    """
    END-002:
    Ensures HbA1c endpoints are measured at biologically plausible time windows.
    """

    category = "Endpoint & Statistical Design"
    code_prefix = "END-HBA1C"

    def should_run(self, protocol: Protocol) -> bool:
        endpoints = protocol.get("endpoints", {})
        return "hba1c" in [e.lower() for e in endpoints.get("all", [])]

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        endpoints = protocol.get("endpoints", {})
        timepoints = endpoints.get("timepoints_weeks", {})
        hba1c_week = timepoints.get("hba1c")

        if hba1c_week is not None and hba1c_week < 16:
            findings.append(
                self.major(
                    "001",
                    f"HbA1c endpoint scheduled at {hba1c_week} weeks, which is earlier than the typical ≥16-week window.",
                    "Extend HbA1c assessment to at least 16 weeks to capture full red blood cell turnover.",
                    "Underestimation or misinterpretation of HbA1c changes, leading to misleading efficacy signals.",
                    context={"hba1c_week": hba1c_week},
                )
            )
        return findings


class SubgroupPowerValidator(BaseValidator):
    """
    END-003:
    Checks whether major subgroups referenced in objectives/statistics
    have corresponding power calculations.
    """

    category = "Endpoint & Statistical Design"
    code_prefix = "END-SUB"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        stats = protocol.get("statistics", {})
        subgroups = stats.get("subgroup_analyses", [])
        subgroup_power = stats.get("subgroup_power", {})

        for sg in subgroups:
            if sg not in subgroup_power:
                findings.append(
                    self.minor(
                        "001",
                        f"Subgroup analysis planned for '{sg}' without explicit power calculation.",
                        "Provide approximate power calculations for key subgroup analyses or clarify that they are exploratory.",
                        "Ambiguity about the interpretability of subgroup results; risk of over-interpretation.",
                        context={"subgroup": sg},
                    )
                )
        return findings


class EndpointClassificationValidator(BaseValidator):
    """
    END-004:
    Ensures endpoints are properly classified as primary/secondary/exploratory.
    """

    category = "Endpoint & Statistical Design"
    code_prefix = "END-CLASS"

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        endpoints = protocol.get("endpoints", {})
        primary = endpoints.get("primary")
        secondary = set(endpoints.get("secondary", []))
        exploratory = set(endpoints.get("exploratory", []))

        if primary and primary in exploratory:
            findings.append(
                self.major(
                    "001",
                    f"Endpoint '{primary}' is simultaneously labelled as primary and exploratory.",
                    "Ensure each endpoint is uniquely classified; move exploratory labels to secondary or remove duplication.",
                    "Confusion about endpoint hierarchy and potential regulatory concerns.",
                    context={"primary": primary},
                )
            )

        # Flag excessive number of primary endpoints
        if isinstance(primary, list) and len(primary) > 2:
            findings.append(
                self.major(
                    "002",
                    f"Protocol lists {len(primary)} primary endpoints, which may dilute statistical focus.",
                    "Limit primary endpoints to a small number and reclassify others as key secondary or exploratory.",
                    "Multiplicity issues, reduced clarity of trial objectives, and difficulties in interpretation.",
                    context={"primary": primary},
                )
            )
        return findings


class AdaptiveDesignPreSpecValidator(BaseValidator):
    """
    END-005:
    Checks that any adaptive or early-stopping language is backed by
    pre-specified statistical rules.
    """

    category = "Endpoint & Statistical Design"
    code_prefix = "END-ADAPT"

    def should_run(self, protocol: Protocol) -> bool:
        stats = protocol.get("statistics", {})
        return bool(stats.get("adaptive_language"))

    def validate(self, protocol: Protocol) -> List[Finding]:
        findings: List[Finding] = []
        stats = protocol.get("statistics", {})
        adaptive_rules = stats.get("adaptive_rules")

        if not adaptive_rules:
            findings.append(
                self.minor(
                    "001",
                    "Protocol references adaptive or early-stopping design but does not provide pre-specified decision rules.",
                    "Specify adaptive decision rules (e.g. stopping boundaries, sample size re-estimation rules) in the SAP.",
                    "Post-hoc scepticism about adaptation decisions and potential regulatory queries.",
                )
            )
        return findings
