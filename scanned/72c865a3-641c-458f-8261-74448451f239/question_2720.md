# Q2720: Untrusted model output deserialized by make_polynomial without validation (biometric_capture/mirror_sweep.rs)

## Question
Can an unprivileged attacker shape the scene so `make_polynomial` in [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) -> `make_polynomial` (function)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `make_polynomial` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `make_polynomial` with malformed/NaN/empty outputs asserting rejection.
