# Q3272: place_decision_deposit can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `place_decision_deposit` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: substrate/frame/referenda/src/lib.rs::place_decision_deposit
- Entrypoint: signed extrinsic `place_decision_deposit`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: Permanent lock of funds or governance queue corruption
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
