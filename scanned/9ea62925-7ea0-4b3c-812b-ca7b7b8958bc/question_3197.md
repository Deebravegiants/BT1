# Q3197: collateral-remove via collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling `amount`, drive `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) — which decrements the map and writes the entry before `send-tokens` executes — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
