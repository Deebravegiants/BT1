# Q3533: receive-tokens via collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling `amount`, drive `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) — which pulls an asset from a named account — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
