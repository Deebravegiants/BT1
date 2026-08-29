# Q3749: merge-price via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the borrower targeted, drive `merge-price` (mainnet/contracts/market/v0-4-market.clar:506) — which attaches a price to an asset record by position in the fold, not by asset id — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:506` -> `merge-price`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `merge-price` attaches a price to an asset record by position in the fold, not by asset id. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the borrower targeted, and assert the attacker's net token balance change is zero or negative.
