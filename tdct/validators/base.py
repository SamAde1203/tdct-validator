# tdct/validators/base.py

from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal

Severity = Literal["CRITICAL", "MAJOR", "MINOR"]

Finding = Dict[str, Any]
Protocol = Dict[str, Any]


class BaseValidator:
    """
    Base class for all TDCT validators.

    Each validator:
    - Decides when to run via `should_run(protocol)`
    - Returns zero or more findings via `validate(protocol)`

    A finding is a dict with:
      - id:   stable ID (e.g. "HUNTER-003" or generic code)
      - code: internal code (e.g. "SAF-HYPO-001")
      - category: domain category (Safety, Eligibility, etc.)
      - severity: CRITICAL / MAJOR / MINOR
      - message: human-readable description of the issue
      - recommendation: suggested fix
      - predicted_outcome: expected consequence if uncorrected
      - context: optional additional structured data
    """

    #: Short name for validator category (e.g. "Safety & Risk Stratification")
    category: str = "General"
    #: Short internal code prefix for findings
    code_prefix: str = "GEN"
    #: Default severity if not overridden
    default_severity: Severity = "MAJOR"

    def should_run(self, protocol: Protocol) -> bool:
        """
        Return True if this validator should run for the given protocol.
        Override in subclasses if you want conditional triggering.
        """
        return True

    def validate(self, protocol: Protocol) -> List[Finding]:
        """
        Implement core validation logic in subclasses.
        Must return a list of Finding dicts.
        """
        raise NotImplementedError

    # Helper builders
    def _finding(
        self,
        code_suffix: str,
        message: str,
        recommendation: str,
        predicted_outcome: str,
        severity: Optional[Severity] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Finding:
        return {
            "code": f"{self.code_prefix}-{code_suffix}",
            "category": self.category,
            "severity": severity or self.default_severity,
            "message": message,
            "recommendation": recommendation,
            "predicted_outcome": predicted_outcome,
            "context": context or {},
        }

    def critical(
        self,
        code_suffix: str,
        message: str,
        recommendation: str,
        predicted_outcome: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Finding:
        return self._finding(
            code_suffix,
            message,
            recommendation,
            predicted_outcome,
            severity="CRITICAL",
            context=context,
        )

    def major(
        self,
        code_suffix: str,
        message: str,
        recommendation: str,
        predicted_outcome: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Finding:
        return self._finding(
            code_suffix,
            message,
            recommendation,
            predicted_outcome,
            severity="MAJOR",
            context=context,
        )

    def minor(
        self,
        code_suffix: str,
        message: str,
        recommendation: str,
        predicted_outcome: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Finding:
        return self._finding(
            code_suffix,
            message,
            recommendation,
            predicted_outcome,
            severity="MINOR",
            context=context,
        )
