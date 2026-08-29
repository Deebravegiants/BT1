# Q1603: subset via repay: leave a residue that no reconciliation pass ever inspects

## Question
`subset` (mainnet/contracts/market/v0-market-vault.clar:100) tests bitmask containment. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing whether the repaid asset is in the accrued debt list, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `subset` tests bitmask containment. Reach it through `repay` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with whether the repaid asset is in the accrued debt list, then read `subset` state before and after in the same block and assert the two sides of the invariant are equal.
