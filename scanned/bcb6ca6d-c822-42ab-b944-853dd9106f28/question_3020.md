# Q3020: Untrusted model output deserialized by from without validation (ai-interface/lib.rs)

## Question
Can an unprivileged attacker shape the scene so `from` in [ai-interface/src/lib.rs](ai-interface/src/lib.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [ai-interface/src/lib.rs](ai-interface/src/lib.rs) -> `from` (function)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `from` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `from` with malformed/NaN/empty outputs asserting rejection.
