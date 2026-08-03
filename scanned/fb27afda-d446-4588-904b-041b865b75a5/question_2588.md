# Q2588: precursor and follow-up calls around set_instance_metadata can exploit intermediate stat

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `set_instance_metadata`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::set_instance_metadata
- Entrypoint: signed extrinsic `set_instance_metadata`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
