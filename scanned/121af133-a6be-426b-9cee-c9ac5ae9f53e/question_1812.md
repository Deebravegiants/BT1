# Q1812: Untrusted model output deserialized by is_correct without validation (python/rgb_net.rs)

## Question
Can an unprivileged attacker shape the scene so `is_correct` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `is_correct` (function)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `is_correct` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `is_correct` with malformed/NaN/empty outputs asserting rejection.
