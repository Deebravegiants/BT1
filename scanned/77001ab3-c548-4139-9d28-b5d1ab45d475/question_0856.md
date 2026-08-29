# Q0856: vault-accrue via redeem: destroy value through a truncation the opposite operation 

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `amount` of shares burned reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it dispatches accrual to one of six vaults by asset id, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `redeem` with `amount` of shares burned, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
