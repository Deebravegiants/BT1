# Q0233: set_collection_metadata can break one-owner / one-item state

## Question
Can an unprivileged attacker call `set_collection_metadata` with crafted amounts, fees, or prices, IDs, hashes, nonces, or location fields so `Collections` and `Instances` disagree about who owns an item, collection right, or wrapped representation?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::set_collection_metadata
- Entrypoint: signed extrinsic `set_collection_metadata`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Target paths where ownership, approval, sale, or wrapper state changes in multiple places and may not commit atomically.
- Invariant to test: Every item must have exactly one effective owner and one coherent authority view across storage.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Exercise transfer, sale, swap, burn, and wrap paths and assert that no duplicate ownership or spendable ghost item remains.
