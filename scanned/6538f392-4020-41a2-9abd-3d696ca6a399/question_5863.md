# Q5863: accrue-debt-asset via repay: make the per-user ledger and the vault aggregate disagree 

## Question
`accrue-debt-asset` (mainnet/contracts/market/v0-4-market.clar:262) calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing whether the repaid asset is in the accrued debt list, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:262` -> `accrue-debt-asset`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `accrue-debt-asset` calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with whether the repaid asset is in the accrued debt list, then read `accrue-debt-asset` state before and after in the same block and assert the two sides of the invariant are equal.
