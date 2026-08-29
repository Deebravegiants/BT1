# Q2668: vault-accrue via deposit: credit one side of an accounting pair without the other

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls whether the vault is at a zero-supply or zero-asset edge reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it credit one side of an accounting pair without the other? Given that it dispatches accrual to one of six vaults by asset id, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `deposit` with whether the vault is at a zero-supply or zero-asset edge, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
