# Q0236: transfer can break one-owner / one-item state

## Question
Can an unprivileged attacker call `transfer` with crafted beneficiary, delegate, or target accounts so `Collections` and `Instances` disagree about who owns an item, collection right, or wrapped representation?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::transfer
- Entrypoint: signed extrinsic `transfer`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Target paths where ownership, approval, sale, or wrapper state changes in multiple places and may not commit atomically.
- Invariant to test: Every item must have exactly one effective owner and one coherent authority view across storage.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Exercise transfer, sale, swap, burn, and wrap paths and assert that no duplicate ownership or spendable ghost item remains.
