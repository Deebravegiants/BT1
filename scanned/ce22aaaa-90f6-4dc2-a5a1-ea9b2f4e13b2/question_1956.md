# Q1956: add-user-scaled-debt via repay: count one deposit as backing for two simultaneous claims

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `add-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:237) in a state where it count one deposit as backing for two simultaneous claims? Given that it adds to the scaled debt row with a graceful u0 default, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:237` -> `add-user-scaled-debt`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `add-user-scaled-debt` adds to the scaled debt row with a graceful u0 default. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount`, including far above the real debt (the capping path) across its boundary values through `repay` in simnet and assert `add-user-scaled-debt` never returns a value that breaks the invariant.
