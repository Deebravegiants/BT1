# Q0801: filter-out-debt-asset via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `amount` used for BOTH the collateral removal and the share redemption, drive `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) — which rebuilds the debt list without one asset, under `as-max-len? ... u64` — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `filter-out-debt-asset` touches, run `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
