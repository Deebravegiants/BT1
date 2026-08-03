# Q2393: precursor and follow-up calls around receive_messages_proof can exploit intermediate sta

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `receive_messages_proof`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: bridges/modules/messages/src/lib.rs::receive_messages_proof
- Entrypoint: public proof / message submission extrinsic `receive_messages_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
