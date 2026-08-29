# Q2677: debt-remove-scaled via collateral-remove: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the `ft` trait principal, drive `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) — which clears the debt bit only when the remaining scaled debt is exactly zero — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with the `ft` trait principal, then read `debt-remove-scaled` state before and after in the same block and assert the two sides of the invariant are equal.
