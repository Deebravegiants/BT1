# Q0112: calc-index-next via repay: destroy value through a truncation the opposite operation 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it applies a multiplier to the current index, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `repay` with whether the repaid asset is in the accrued debt list, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
