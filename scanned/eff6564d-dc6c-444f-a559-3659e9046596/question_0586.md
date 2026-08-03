# Q0586: submit_parachain_heads_ex can regress best-known bridge state

## Question
Can an unprivileged attacker use `submit_parachain_heads_ex` to make `BestParaHeadHash` accept older or conflicting data after newer data is already finalized?

## Target
- File/function: bridges/modules/parachains/src/lib.rs::submit_parachain_heads_ex
- Entrypoint: public proof / message submission extrinsic `submit_parachain_heads_ex`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Test stale-but-well-formed proofs and alternate branches around monotonicity checks.
- Invariant to test: Best-known bridged state must advance monotonically and never regress under public input.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Submit a newer valid object first, then try older or conflicting variants and assert no rollback or overwrite occurs.
