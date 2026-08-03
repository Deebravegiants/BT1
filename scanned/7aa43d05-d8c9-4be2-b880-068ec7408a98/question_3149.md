# Q3149: bond_extra_other can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `bond_extra_other` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::bond_extra_other
- Entrypoint: signed extrinsic `bond_extra_other`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
