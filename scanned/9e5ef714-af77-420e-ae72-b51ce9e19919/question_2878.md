# Q2878: unpack-u16 via call-ststx-ratio: have the same quantity scaled twice by two contracts that 

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling whether the ratio is fetched before or after other state changes in the block, can an unprivileged attacker make `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) have the same quantity scaled twice by two contracts that round differently? `unpack-u16` unpacks eight u16 curve fields from one packed word, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `call-ststx-ratio` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `call-ststx-ratio` with whether the ratio is fetched before or after other state changes in the block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
