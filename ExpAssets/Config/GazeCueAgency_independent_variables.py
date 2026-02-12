from klibs.KLStructure import FactorSet

exp_factors = FactorSet(
    {
        'cue_type': ['frame', 'human', 'robot', 'schema'],
        'cued_side': ['left', 'right', 'neutral'],
        'target_location': ['left', 'right'],
    }
)
