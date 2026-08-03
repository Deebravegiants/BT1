# Q3068: call_old_weight can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `call_old_weight` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::call_old_weight
- Entrypoint: public VM / contract execution extrinsic `call_old_weight`
- Attacker controls: nested call payloads, amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: Chain halt / block-production slowdown from undercharged VM execution
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
