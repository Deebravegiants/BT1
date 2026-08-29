# Q3108: write-feed via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it applies one Pyth price-feed update and folds its status, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `supply-collateral-add` in simnet and assert `write-feed` never returns a value that breaks the invariant.
