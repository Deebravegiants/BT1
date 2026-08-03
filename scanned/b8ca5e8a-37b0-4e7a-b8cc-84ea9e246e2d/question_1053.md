# Q1053: burn can desync supply caps from live items

## Question
Can an unprivileged attacker call `burn` in a way that makes minted, burned, wrapped, or deleted item counts diverge from the effective collection supply cap or wrapper issuance?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::burn
- Entrypoint: signed extrinsic `burn`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Stress create, mint, burn, delete, and wrap paths around exact limits and failure edges.
- Invariant to test: Collection or wrapper supply must stay consistent with every live item and every redeemable fraction.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Fuzz exact-cap and cap-plus-one transitions and test whether further minting, buying, or unifying behaves correctly.
