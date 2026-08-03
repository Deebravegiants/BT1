# Q1086: create_collection can desync supply caps from live items

## Question
Can an unprivileged attacker call `create_collection` in a way that makes minted, burned, wrapped, or deleted item counts diverge from the effective collection supply cap or wrapper issuance?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::create_collection
- Entrypoint: signed extrinsic `create_collection`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Stress create, mint, burn, delete, and wrap paths around exact limits and failure edges.
- Invariant to test: Collection or wrapper supply must stay consistent with every live item and every redeemable fraction.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Fuzz exact-cap and cap-plus-one transitions and test whether further minting, buying, or unifying behaves correctly.
