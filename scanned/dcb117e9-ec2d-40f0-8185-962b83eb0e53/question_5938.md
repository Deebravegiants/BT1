# Q5938: resolve-callcode via borrow: credit one side of an accounting pair without the other

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `price-feeds` buffers, can an unprivileged attacker make `resolve-callcode` (mainnet/contracts/market/v0-4-market.clar:349) credit one side of an accounting pair without the other? `resolve-callcode` chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:349` -> `resolve-callcode`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `resolve-callcode` chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `borrow` with the `price-feeds` buffers, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
