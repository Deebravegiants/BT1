# Q3245: set_collection_metadata can drift from benchmark assumptions on rare valid inputs

## Question
Can an unprivileged attacker use a rare but valid input shape to `set_collection_metadata` that is substantially more expensive than the benchmarked path, making public abuse viable?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_collection_metadata
- Entrypoint: signed extrinsic `set_collection_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Benchmarks often miss degenerate but valid shapes such as maximal duplicates, deep nesting, stale cleanup mixes, or empty/non-empty transitions.
- Invariant to test: All valid public input shapes must stay within the charged worst-case resource envelope.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Generate adversarial but valid shapes that differ structurally from the benchmark happy path and compare actual execution cost.
