# Q3865: get-position via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling the trait principals supplied per entry, drive `get-position` (mainnet/contracts/market/v0-4-market.clar:466) — which returns only rows whose bit is set in the ENABLED bitmap — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with the trait principals supplied per entry, then read `get-position` state before and after in the same block and assert the two sides of the invariant are equal.
