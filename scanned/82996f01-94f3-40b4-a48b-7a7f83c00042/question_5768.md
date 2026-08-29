# Q5768: mask-update via collateral-add: record a repayment larger than the value actually delivere

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the `ft` trait principal reach `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) in a state where it record a repayment larger than the value actually delivered? Given that it sets or clears one bit, clearing only when the row reaches exactly zero, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the `ft` trait principal varied, and assert that the value `mask-update` returns is identical in both runs; a divergence confirms the finding.
