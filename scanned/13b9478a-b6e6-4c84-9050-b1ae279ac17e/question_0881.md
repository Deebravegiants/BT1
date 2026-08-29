# Q0881: resolve-interpolation-points via collateral-add: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling whether this asset is already collateral (the is-new-collateral branch), drive `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) — which selects the bracketing curve points for a utilization — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with whether this asset is already collateral (the is-new-collateral branch), and assert the attacker's net token balance change is zero or negative.
