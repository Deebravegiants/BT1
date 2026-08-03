# Q2394: precursor and follow-up calls around submit_parachain_heads can exploit intermediate sta

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `submit_parachain_heads`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: bridges/modules/parachains/src/lib.rs::submit_parachain_heads
- Entrypoint: public proof / message submission extrinsic `submit_parachain_heads`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
