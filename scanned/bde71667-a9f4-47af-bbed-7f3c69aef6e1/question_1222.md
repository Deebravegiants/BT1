# Q1222: is-healthy via collateral-remove: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the `price-feeds` buffers, can an unprivileged attacker make `is-healthy` (mainnet/contracts/market/v0-4-market.clar:656) record a repayment larger than the value actually delivered? `is-healthy` returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:656` -> `is-healthy`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `is-healthy` returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove` with the `price-feeds` buffers, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
