# Q3064: submit_parachain_heads_ex can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `submit_parachain_heads_ex` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: bridges/modules/parachains/src/lib.rs::submit_parachain_heads_ex
- Entrypoint: public proof / message submission extrinsic `submit_parachain_heads_ex`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
