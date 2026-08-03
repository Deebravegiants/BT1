# Q2611: precursor and follow-up calls around reap_page can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `reap_page`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::reap_page
- Entrypoint: public message maintenance extrinsic `reap_page`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Repeated execution, fee burn mismatch, or message payout duplication
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
