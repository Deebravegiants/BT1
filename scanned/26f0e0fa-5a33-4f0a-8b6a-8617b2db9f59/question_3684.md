# Q3684: calc-multiplier-delta via repay: make the per-user ledger and the vault aggregate disagree 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls the `ft` trait principal reach `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it compounds a rate over `time-delta` with a caller-independent rounding flag, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `repay` in simnet and assert `calc-multiplier-delta` never returns a value that breaks the invariant.
