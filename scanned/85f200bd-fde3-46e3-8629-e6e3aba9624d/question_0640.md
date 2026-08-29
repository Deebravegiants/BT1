# Q0640: accrue-user-collateral via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls remaining zToken collateral whose price moves with the redeem reach `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it accrues only rows that `is-ztoken` recognises, skipping everything else, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
