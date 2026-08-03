# Q0202: create_swap can break one-owner / one-item state

## Question
Can an unprivileged attacker call `create_swap` with crafted call repetition, batching order, and surrounding state so `Collection` and `Item` disagree about who owns an item, collection right, or wrapped representation?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::create_swap
- Entrypoint: signed extrinsic `create_swap`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Target paths where ownership, approval, sale, or wrapper state changes in multiple places and may not commit atomically.
- Invariant to test: Every item must have exactly one effective owner and one coherent authority view across storage.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Exercise transfer, sale, swap, burn, and wrap paths and assert that no duplicate ownership or spendable ghost item remains.
