# Q3169: add-user-collateral via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the borrower targeted, drive `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) — which adds to the collateral row with a graceful u0 default — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the borrower targeted, then read `add-user-collateral` state before and after in the same block and assert the two sides of the invariant are equal.
