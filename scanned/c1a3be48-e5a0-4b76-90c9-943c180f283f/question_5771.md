# Q5771: accrue-user-debts via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
`accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) folds accrual over the position's debt list only. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the `price-feeds` buffers, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with the `price-feeds` buffers, and assert the attacker's net token balance change is zero or negative.
