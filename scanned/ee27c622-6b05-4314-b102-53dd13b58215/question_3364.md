# Q3364: oracle-timestamp-fresh via collateral-remove-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `min-underlying` reach `oracle-timestamp-fresh` (mainnet/contracts/market/v0-4-market.clar:365) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:365` -> `oracle-timestamp-fresh`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `oracle-timestamp-fresh` sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`. Reach it through `collateral-remove-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `min-underlying`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
