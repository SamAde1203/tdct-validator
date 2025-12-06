TDCT – Trial Design Consistency Testing
Automated protocol validation for clinical trials
Overview

TDCT (Trial Design Consistency Testing) is a computational framework for detecting logical, methodological, and safety-related design flaws in clinical trial protocols before human participants are enrolled.

It was developed as part of:

Adeyemi S. (2025). Automated Trial Design Consistency Testing (TDCT):
A Validation System for Identifying Protocol Design Flaws Before Clinical Trial Initiation.

TDCT encodes protocol-design best practices into modular, domain-specific validators — similar to unit tests — enabling systematic, reproducible protocol quality assurance.

Key Features
✔ Automated protocol scanning

Transforms protocol text into structured YAML and runs more than 20 validation modules.

✔ Detects critical design flaws

Identifies safety gaps, endpoint contradictions, dosing inconsistencies, and measurement errors.

✔ Validated on real-world trials

TDCT has been demonstrated on:

HUNTER – Phase Ib/IIa, diabetes (prospective)

ACCORD – Phase III, diabetes (retrospective)

SPRINT – Phase III, hypertension (retrospective)

✔ High impact potential

Retrospective analysis shows TDCT would have helped prevent:

Early termination of ACCORD (≈$45M USD loss)

SPRINT blood-pressure measurement controversy

Safety risks in the first-in-human HUNTER trial

Repository Structure
tdct/
  validators/        # Core validators (safety, eligibility, endpoints, measurement, regulatory)
  runner.py          # Main entry point for executing validations
  schema/            # YAML schema definitions for trial protocols
protocols/           # YAML protocol files (public, synthetic, or redacted)
findings/            # TDCT outputs from exemplar trials
examples/            # Example inputs/outputs for users

Installation
git clone https://github.com/<YOUR_USERNAME>/tdct-validator.git
cd tdct-validator
pip install -r requirements.txt

Running TDCT

Validate any protocol YAML file:

python tdct/runner.py --protocol protocols/hunter_protocol.yaml


Output will be generated in:

/findings/


(JSON format)

YAML Protocol Format (Simplified)
eligibility:
  age_min: 30
  age_max: 60
  exclusions:
    - severe_hypoglycemia_12m

intervention:
  doses:
    - 500mg
    - 1000mg
    - 1500mg

endpoints:
  primary: safety
  secondary:
    - HbA1c
    - fasting_glucose

measurement:
  BP_method: "not_specified"

Example Validator (Safety)
class HypoglycemiaRiskValidator(BaseValidator):
    trigger = lambda p: p.population.age_max >= 65 and p.intervention.glucose_lowering

    def validate(self, protocol):
        exclusion = protocol.eligibility.exclusions
        if "severe_hypoglycemia_24m" not in exclusion:
            return self.critical(
                code="SAF-001",
                message="Missing severe hypoglycemia exclusion (24 months).",
                recommendation="Add exclusion: severe hypoglycemia within 24 months.",
                predicted_outcome="High risk of mortality in elderly on glucose-lowering therapy."
            )

Contributing

Contributions are welcome, including:

New validators

YAML schema extensions

NLP-based auto-extraction tools

Therapeutic area–specific validator sets (oncology, CNS, paediatrics)

Please submit a Pull Request or open an Issue.

License

Released under the MIT License.
Commercial use permitted with attribution.

Citation

A CITATION.cff file is included for GitHub’s citation engine.

cff-version: 1.2.0
title: TDCT – Trial Design Consistency Testing
authors:
  - family-names: Adeyemi
    given-names: Sam
version: 1.0.0
doi: 10.5281/zenodo.xxxxxxx
message: "Please cite this project if you use TDCT."

