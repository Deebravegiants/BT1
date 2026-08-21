# Q2750: Untrusted model output deserialized by Configuration without validation (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker shape the scene so `Configuration` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `Configuration` (type)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `Configuration` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `Configuration` with malformed/NaN/empty outputs asserting rejection.
