# Q3166: withdraw_unbonded can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `withdraw_unbonded` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::withdraw_unbonded
- Entrypoint: signed extrinsic `withdraw_unbonded`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
