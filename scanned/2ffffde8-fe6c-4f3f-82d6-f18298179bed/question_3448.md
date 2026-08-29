# Q3448: find-and-resolve-asset-value via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the `ft` trait principal reach `find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reuses an already-resolved price from the asset list and returns u0 when the asset is not found, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-add` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
