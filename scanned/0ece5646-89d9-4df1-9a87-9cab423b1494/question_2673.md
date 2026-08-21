# Q2673: Untrusted model output deserialized by update_occlusion without validation (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker shape the scene so `update_occlusion` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `update_occlusion` (function)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `update_occlusion` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `update_occlusion` with malformed/NaN/empty outputs asserting rejection.
