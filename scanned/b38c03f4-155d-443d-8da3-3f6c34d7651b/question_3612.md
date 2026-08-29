# Q3612: iter-find-superset via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `ft` trait principal reach `iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it short-circuits on the first superset match, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `collateral-remove` in simnet and assert `iter-find-superset` never returns a value that breaks the invariant.
