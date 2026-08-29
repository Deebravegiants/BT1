# Q5928: interest-rate via repay: have the same quantity scaled twice by two contracts that 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `on-behalf-of`, naming any third-party principal reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it interpolates the packed curve at the current utilization, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `on-behalf-of`, naming any third-party principal across its boundary values through `repay` in simnet and assert `interest-rate` never returns a value that breaks the invariant.
