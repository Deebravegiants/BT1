# Q2924: Untrusted model output deserialized by is_valid without validation (face_identifier/mod.rs)

## Question
Can an unprivileged attacker shape the scene so `is_valid` in [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) -> `is_valid` (function)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `is_valid` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `is_valid` with malformed/NaN/empty outputs asserting rejection.
