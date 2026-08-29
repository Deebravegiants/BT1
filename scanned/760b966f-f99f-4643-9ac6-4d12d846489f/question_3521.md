# Q3521: receive-tokens via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling the zToken/underlying id mapping reached (the u100 sentinel branch), drive `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) — which pulls an asset from a named account — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with the zToken/underlying id mapping reached (the u100 sentinel branch), and assert the attacker's net token balance change is zero or negative.
