# Q0581: submit_finality_proof can regress best-known bridge state

## Question
Can an unprivileged attacker use `submit_finality_proof` to make `BestFinalized` accept older or conflicting data after newer data is already finalized?

## Target
- File/function: bridges/modules/grandpa/src/lib.rs::submit_finality_proof
- Entrypoint: public proof / message submission extrinsic `submit_finality_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Test stale-but-well-formed proofs and alternate branches around monotonicity checks.
- Invariant to test: Best-known bridged state must advance monotonically and never regress under public input.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Submit a newer valid object first, then try older or conflicting variants and assert no rollback or overwrite occurs.
