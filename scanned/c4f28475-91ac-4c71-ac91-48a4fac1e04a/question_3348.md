# Q3348: get-available-assets via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `supply-collateral-add` in simnet and assert `get-available-assets` never returns a value that breaks the invariant.
