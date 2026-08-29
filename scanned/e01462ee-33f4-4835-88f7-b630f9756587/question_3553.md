# Q3553: vault-system-repay via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling the trait principals supplied per entry, drive `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) — which routes a repayment to one of six vaults by asset id — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with the trait principals supplied per entry, then read `vault-system-repay` state before and after in the same block and assert the two sides of the invariant are equal.
