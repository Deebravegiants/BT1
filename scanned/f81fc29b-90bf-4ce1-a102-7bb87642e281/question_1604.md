# Q1604: Untrusted model output deserialized by EyePipeline without validation (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker shape the scene so `EyePipeline` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `EyePipeline` (type)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `EyePipeline` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `EyePipeline` with malformed/NaN/empty outputs asserting rejection.
