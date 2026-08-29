# Q2002: debt-remove-scaled via repay: have the same quantity scaled twice by two contracts that 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling whether the repaid asset is in the accrued debt list, can an unprivileged attacker make `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) have the same quantity scaled twice by two contracts that round differently? `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `repay` with whether the repaid asset is in the accrued debt list, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
