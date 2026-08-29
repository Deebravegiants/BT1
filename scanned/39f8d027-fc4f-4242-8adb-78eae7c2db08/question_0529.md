# Q0529: filter-out-debt-asset via collateral-add: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the `ft` trait principal, drive `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) — which rebuilds the debt list without one asset, under `as-max-len? ... u64` — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the `ft` trait principal, then read `filter-out-debt-asset` state before and after in the same block and assert the two sides of the invariant are equal.
