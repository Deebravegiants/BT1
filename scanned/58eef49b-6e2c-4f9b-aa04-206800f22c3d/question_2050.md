# Q2050: vault-system-repay via repay: have the same quantity scaled twice by two contracts that 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling whether the repaid asset is in the accrued debt list, can an unprivileged attacker make `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) have the same quantity scaled twice by two contracts that round differently? `vault-system-repay` routes a repayment to one of six vaults by asset id, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `repay` with whether the repaid asset is in the accrued debt list, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
