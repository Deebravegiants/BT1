# Q3468: vault-system-repay via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it routes a repayment to one of six vaults by asset id, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `borrow` in simnet and assert `vault-system-repay` never returns a value that breaks the invariant.
