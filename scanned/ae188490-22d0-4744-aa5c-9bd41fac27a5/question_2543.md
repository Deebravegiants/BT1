# Q2543: precursor and follow-up calls around remove_proxy can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `remove_proxy`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::remove_proxy
- Entrypoint: public dispatch wrapper `remove_proxy`
- Attacker controls: nested call payloads, beneficiary, delegate, or target accounts, batched or wrapped execution context
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
