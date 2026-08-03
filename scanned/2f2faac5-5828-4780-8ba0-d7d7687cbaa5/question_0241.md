# Q0241: clear_attribute can break one-owner / one-item state

## Question
Can an unprivileged attacker call `clear_attribute` with crafted IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering so `Collection` and `Asset` disagree about who owns an item, collection right, or wrapped representation?

## Target
- File/function: substrate/frame/uniques/src/lib.rs::clear_attribute
- Entrypoint: signed extrinsic `clear_attribute`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Target paths where ownership, approval, sale, or wrapper state changes in multiple places and may not commit atomically.
- Invariant to test: Every item must have exactly one effective owner and one coherent authority view across storage.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Exercise transfer, sale, swap, burn, and wrap paths and assert that no duplicate ownership or spendable ghost item remains.
