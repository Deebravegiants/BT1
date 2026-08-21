# Q0332: Untrusted model output deserialized by continuous_calibration without validation (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker shape the scene so `continuous_calibration` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `continuous_calibration` (function)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `continuous_calibration` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `continuous_calibration` with malformed/NaN/empty outputs asserting rejection.
