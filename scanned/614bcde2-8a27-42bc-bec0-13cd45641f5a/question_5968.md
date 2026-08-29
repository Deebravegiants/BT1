# Q5968: calc-treasury-lp-preview via redeem: have the same quantity scaled twice by two contracts that 

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the vault's available liquidity relative to the redemption reach `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `redeem` with the vault's available liquidity relative to the redemption, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
