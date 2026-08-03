# Q2484: precursor and follow-up calls around claim_payout_other can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `claim_payout_other`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::claim_payout_other
- Entrypoint: signed extrinsic `claim_payout_other`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
