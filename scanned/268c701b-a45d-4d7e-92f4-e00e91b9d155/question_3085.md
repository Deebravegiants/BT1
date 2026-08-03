# Q3085: create_pool can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `create_pool` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::create_pool
- Entrypoint: signed extrinsic `create_pool`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
