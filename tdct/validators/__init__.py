# tdct/validators/__init__.py

from .base import BaseValidator

from .safety_validators import (
    HypoglycemiaRiskValidator,
    FirstInHumanDoseEscalationValidator,
    AEExclusionCoverageValidator,
    DDIDrugInteractionValidator,
)

from .eligibility_validators import (
    AgeRangeConsistencyValidator,
    TreatmentNaiveDefinitionValidator,
    ComorbidityLogicValidator,
    HouseholdExclusionBiasValidator,
    OverlyRestrictiveGeneralizabilityValidator,
    ElderlyUpperAgeJustificationValidator,
)

from .endpoint_validators import (
    PrimaryEndpointPowerAlignmentValidator,
    HbA1cTimingValidator,
    SubgroupPowerValidator,
    EndpointClassificationValidator,
    AdaptiveDesignPreSpecValidator,
)

from .measurement_validators import (
    BPMeasurementStandardisationValidator,
    LifestyleInterventionStandardisationValidator,
    BiomarkerAssaySpecificationValidator,
)

from .regulatory_validators import (
    PhaseDesignationValidator,
    ConsentSubstudyHierarchyValidator,
)


ALL_VALIDATORS = [
    # Safety (4)
    HypoglycemiaRiskValidator(),
    FirstInHumanDoseEscalationValidator(),
    AEExclusionCoverageValidator(),
    DDIDrugInteractionValidator(),

    # Eligibility (6)
    AgeRangeConsistencyValidator(),
    TreatmentNaiveDefinitionValidator(),
    ComorbidityLogicValidator(),
    HouseholdExclusionBiasValidator(),
    OverlyRestrictiveGeneralizabilityValidator(),
    ElderlyUpperAgeJustificationValidator(),

    # Endpoint & Statistical (5)
    PrimaryEndpointPowerAlignmentValidator(),
    HbA1cTimingValidator(),
    SubgroupPowerValidator(),
    EndpointClassificationValidator(),
    AdaptiveDesignPreSpecValidator(),

    # Measurement & Standardisation (3)
    BPMeasurementStandardisationValidator(),
    LifestyleInterventionStandardisationValidator(),
    BiomarkerAssaySpecificationValidator(),

    # Regulatory & Design Classification (2)
    PhaseDesignationValidator(),
    ConsentSubstudyHierarchyValidator(),
]
