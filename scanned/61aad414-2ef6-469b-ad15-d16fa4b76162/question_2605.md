# Q2605: precursor and follow-up calls around refund_submission_deposit can exploit intermediate

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `refund_submission_deposit`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/referenda/src/lib.rs::refund_submission_deposit
- Entrypoint: signed extrinsic `refund_submission_deposit`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
