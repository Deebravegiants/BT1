# Q3916: get-cached-indexes via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with vault share price at the moment of the deposit leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
