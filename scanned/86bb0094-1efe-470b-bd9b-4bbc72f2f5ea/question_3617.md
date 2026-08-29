# Q3617: convert-to-assets-preview via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling remaining zToken collateral whose price moves with the redeem, drive `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) — which prices a redemption against `total-assets-preview` and `total-supply-preview` — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with remaining zToken collateral whose price moves with the redeem, and assert the attacker's net token balance change is zero or negative.
