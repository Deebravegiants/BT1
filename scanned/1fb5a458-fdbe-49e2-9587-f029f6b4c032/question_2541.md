# Q2541: precursor and follow-up calls around remove_announcement can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `remove_announcement`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::remove_announcement
- Entrypoint: public dispatch wrapper `remove_announcement`
- Attacker controls: batched or wrapped execution context
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
