# Q3026: Untrusted model output deserialized by IrNet without validation (ir-net/lib.rs)

## Question
Can an unprivileged attacker shape the scene so `IrNet` in [ir-net/src/lib.rs](ir-net/src/lib.rs) receives model output with unexpected shape, length, or NaN content that is consumed without validation, corrupting the derived biometric code or verdict?

## Target
- File/function: [ir-net/src/lib.rs](ir-net/src/lib.rs) -> `IrNet` (type)
- Entrypoint: Camera scene driving the inference agent
- Attacker controls: scene content controlling model output distribution and shape
- Exploit idea: Check `IrNet` for shape/range/finiteness validation before use of the tensor/struct fields.
- Invariant to test: Every model output is validated for shape, range, and finiteness before it influences a decision.
- Expected Immunefi impact: Corrupted biometric code or bypassed verdict from degenerate inference output
- Fast validation: Unit-test `IrNet` with malformed/NaN/empty outputs asserting rejection.
