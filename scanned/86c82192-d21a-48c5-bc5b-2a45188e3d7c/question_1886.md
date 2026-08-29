# Q1886: normalize via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `min-underlying`, can an unprivileged attacker make `normalize` (mainnet/contracts/market/v0-4-market.clar:576) record a repayment larger than the value actually delivered? `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:576` -> `normalize`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `min-underlying` varied, and assert that the value `normalize` returns is identical in both runs; a divergence confirms the finding.
