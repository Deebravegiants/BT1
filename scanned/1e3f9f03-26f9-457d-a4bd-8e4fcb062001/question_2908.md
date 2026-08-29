# Q2908: vault-accrue via accrue: credit one side of an accounting pair without the other

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls whether an earlier call in the same block already advanced last-update reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it credit one side of an accounting pair without the other? Given that it dispatches accrual to one of six vaults by asset id, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `accrue` with whether an earlier call in the same block already advanced last-update, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
