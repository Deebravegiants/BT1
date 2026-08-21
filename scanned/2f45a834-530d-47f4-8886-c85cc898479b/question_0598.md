# Q0598: Untrusted model output deserialized by FIIsValidOutput without validation (face_identifier/types.rs)

## Question
Can an unprivileged attacker shape the scene so `FIIsValidOutput` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `FIIsValidOutput` (type)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `FIIsValidOutput` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `FIIsValidOutput` with malformed/NaN/empty outputs asserting rejection.
