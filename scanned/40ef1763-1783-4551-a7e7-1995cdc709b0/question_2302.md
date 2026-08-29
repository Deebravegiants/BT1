# Q2302: send-underlying via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling vault share price at the moment of the deposit leg, can an unprivileged attacker make `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) have the same quantity scaled twice by two contracts that round differently? `send-underlying` pushes the underlying under an `as-contract?` post-condition scope, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with vault share price at the moment of the deposit leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
