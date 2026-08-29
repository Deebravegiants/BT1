# Q2834: accrue-user-debts via borrow: have the same quantity scaled twice by two contracts that 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `price-feeds` buffers, can an unprivileged attacker make `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) have the same quantity scaled twice by two contracts that round differently? `accrue-user-debts` folds accrual over the position's debt list only, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `price-feeds` buffers varied, and assert that the value `accrue-user-debts` returns is identical in both runs; a divergence confirms the finding.
