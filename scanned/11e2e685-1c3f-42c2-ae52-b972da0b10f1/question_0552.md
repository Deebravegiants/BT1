# Q0552: filter-out-debt-asset via borrow: destroy value through a truncation the opposite operation 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the order of accrual versus price resolution inside the let reach `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it rebuilds the debt list without one asset, under `as-max-len? ... u64`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the order of accrual versus price resolution inside the let across its boundary values through `borrow` in simnet and assert `filter-out-debt-asset` never returns a value that breaks the invariant.
