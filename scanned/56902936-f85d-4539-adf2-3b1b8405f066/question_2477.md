# Q2477: precursor and follow-up calls around poke_deposit can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `poke_deposit`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/indices/src/lib.rs::poke_deposit
- Entrypoint: signed extrinsic `poke_deposit`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
