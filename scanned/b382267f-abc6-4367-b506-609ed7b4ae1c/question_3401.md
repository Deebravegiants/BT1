# Q3401: calc-liquidation-params via liquidate: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `debt-amount`, drive `calc-liquidation-params` (mainnet/contracts/market/v0-4-market.clar:739) — which chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:739` -> `calc-liquidation-params`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `calc-liquidation-params` chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `debt-amount`, and assert the attacker's net token balance change is zero or negative.
