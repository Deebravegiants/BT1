# Q1548: system-borrow via repay: count one deposit as backing for two simultaneous claims

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `system-borrow` (mainnet/contracts/vault/v0-vault-stx.clar:865) in a state where it count one deposit as backing for two simultaneous claims? Given that it independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:865` -> `system-borrow`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `system-borrow` independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount`, including far above the real debt (the capping path) across its boundary values through `repay` in simnet and assert `system-borrow` never returns a value that breaks the invariant.
