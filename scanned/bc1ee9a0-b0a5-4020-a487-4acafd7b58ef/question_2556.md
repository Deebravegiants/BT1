# Q2556: precursor and follow-up calls around if_else can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `if_else`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/utility/src/lib.rs::if_else
- Entrypoint: public dispatch wrapper `if_else`
- Attacker controls: nested call payloads, batched or wrapped execution context
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
