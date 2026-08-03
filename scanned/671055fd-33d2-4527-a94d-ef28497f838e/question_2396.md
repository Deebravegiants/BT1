# Q2396: precursor and follow-up calls around submit can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `submit`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: bridges/snowbridge/pallets/inbound-queue/src/lib.rs::submit
- Entrypoint: public proof / message submission extrinsic `submit`
- Attacker controls: proof or signed payload contents
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
