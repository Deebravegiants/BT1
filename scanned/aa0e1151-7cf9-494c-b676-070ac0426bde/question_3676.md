# Q3676: get-position via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the `ft` trait principal reach `get-position` (mainnet/contracts/market/v0-4-market.clar:466) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it returns only rows whose bit is set in the ENABLED bitmap, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-add` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
