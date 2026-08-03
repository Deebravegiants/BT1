# Q2546: precursor and follow-up calls around control_inherited_account can exploit intermediate

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `control_inherited_account`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::control_inherited_account
- Entrypoint: signed extrinsic `control_inherited_account`
- Attacker controls: nested call payloads
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
