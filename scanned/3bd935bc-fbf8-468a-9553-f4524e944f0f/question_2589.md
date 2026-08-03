# Q2589: precursor and follow-up calls around set_item_metadata can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `set_item_metadata`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::set_item_metadata
- Entrypoint: signed extrinsic `set_item_metadata`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
