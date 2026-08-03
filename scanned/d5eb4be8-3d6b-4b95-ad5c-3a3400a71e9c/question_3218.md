# Q3218: revoke_inheritor can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `revoke_inheritor` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::revoke_inheritor
- Entrypoint: signed extrinsic `revoke_inheritor`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: State corruption or underpriced wrapped execution leading to chain degradation
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
