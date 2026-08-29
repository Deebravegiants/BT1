# Q2956: mask-update via repay: make the per-user ledger and the vault aggregate disagree 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls the `ft` trait principal reach `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it sets or clears one bit, clearing only when the row reaches exactly zero, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `repay` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
