# Q3809: resolve-interpolation-points via liquidate: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `debt-amount`, drive `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) — which selects the bracketing curve points for a utilization — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `debt-amount`, and assert the attacker's net token balance change is zero or negative.
