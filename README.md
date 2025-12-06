# TDCT – Trial Design Consistency Testing  
[![DOI](https://zenodo.org/badge/1111392599.svg)](https://doi.org/10.5281/zenodo.17844210)

Automated, reproducible protocol validation for detecting methodological, logical, and safety-related flaws in clinical trial protocols **before** participant enrolment.

TDCT was developed as part of the research paper:

**Adeyemi S. (2025)**  
*Automated Trial Design Consistency Testing (TDCT): A Validation System for Identifying Protocol Design Flaws Before Clinical Trial Initiation.*

---

## 📌 Overview

TDCT (Trial Design Consistency Testing) is a modular, validator-driven framework that performs **unit-test–style checks** on clinical trial protocols.  
It converts protocol content into structured YAML and automatically evaluates:

- Safety logic  
- Eligibility rules  
- Endpoint consistency  
- Intervention design  
- Measurement standardisation  
- Regulatory/operational risks  

This makes protocol review **systematic, reproducible, and computational** instead of manual-only.

---

## ⭐ Key Features

### ✔ Automated Protocol Scanning
Converts raw protocol text into structured YAML and runs >20 validators.

### ✔ Detects Critical Design Flaws
Identifies:
- safety gaps  
- endpoint contradictions  
- dosing errors  
- missing exclusions  
- measurement inconsistencies  
- improper classifications  

### ✔ Validated on Real Clinical Trials
TDCT was tested on:

| Trial | Phase | N | Findings |
|-------|-------|------|----------|
| **HUNTER** | Ib/IIa | 60 | 7 findings |
| **ACCORD** | III | 10,251 | 5 findings |
| **SPRINT** | III | 9,361 | 7 findings |

### ✔ Research Impact
Retrospective validation shows TDCT could have *prevented or flagged*:

- Early ACCORD termination (USD 45M impact)  
- SPRINT BP measurement controversy  
- Safety risks in the first-in-human HUNTER trial  

---

## 📁 Repository Structure

tdct-validator/
│
├── tdct/
│ ├── init.py
│ ├── runner.py
│ ├── utils.py
│ ├── validators/
│ └── schema/
│
├── protocols/
│ ├── hunter_protocol.yaml
│ ├── accord_protocol.yaml
│ └── sprint_protocol.yaml
│
├── findings/
│ ├── hunter_findings.json
│ ├── accord_findings.json
│ └── sprint_findings.json
│
├── examples/
│ ├── example_input.yaml
│ └── example_output.json
│
├── CITATION.cff
├── requirements.txt
├── LICENSE
└── README.md

yaml
Copy code

---

## ⚙ Installation

```bash
git clone https://github.com/SamAde1203/tdct-validator.git
cd tdct-validator
pip install -r requirements.txt
▶ Running TDCT
Validate any protocol YAML:

bash
Copy code
python tdct/runner.py --protocol protocols/hunter_protocol.yaml
Findings will be saved to findings/ in JSON format.

🧩 Example YAML (Simplified)
yaml
Copy code
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
🔍 Example Safety Validator
python
Copy code
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
📜 License
TDCT is released under the MIT License.
Commercial and academic use permitted with attribution.

📖 Citation
If you use TDCT in your research, please cite:

scss
Copy code
Adeyemi, S. (2025).
TDCT – Trial Design Consistency Testing (Version 1.0.0) [Computer software].
Zenodo. https://doi.org/10.5281/zenodo.17844210
🧾 Software Availability Statement (for your paper)
TDCT v1.0.0 is openly available under the MIT License at:

GitHub: https://github.com/SamAde1203/tdct-validator

Zenodo archive (DOI): https://doi.org/10.5281/zenodo.17844210

All protocol schemas, validators, and replication files for HUNTER, ACCORD, and SPRINT are included in the release.

🤝 Contributing
We welcome contributions including:

New validators

Auto-extraction NLP modules

Protocol schemas

TA-specific validator packs (oncology, CNS, paediatrics)

Submit a pull request or open an issue.

🙏 Acknowledgments
TDCT was created independently by Sam Adeyemi, MSc (UK).
No institutional funding was used.

Public protocol sources: ClinicalTrials.gov
