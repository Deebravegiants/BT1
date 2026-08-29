# Q2660: vault-accrue via borrow: credit one side of an accounting pair without the other

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `price-feeds` buffers reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it credit one side of an accounting pair without the other? Given that it dispatches accrual to one of six vaults by asset id, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `price-feeds` buffers varied, and assert that the value `vault-accrue` returns is identical in both runs; a divergence confirms the finding.
