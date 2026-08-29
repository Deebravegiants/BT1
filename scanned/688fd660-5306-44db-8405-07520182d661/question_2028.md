# Q2028: resolve-interpolation-points via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the position state the final collateral-add is validated against reach `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) in a state where it credit one side of an accounting pair without the other? Given that it selects the bracketing curve points for a utilization, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the position state the final collateral-add is validated against across its boundary values through `supply-collateral-add` in simnet and assert `resolve-interpolation-points` never returns a value that breaks the invariant.
