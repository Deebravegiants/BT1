# Q2700: principal-ratio-reduction via accrue: credit one side of an accounting pair without the other

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:406) in a state where it credit one side of an accounting pair without the other? Given that it derives a principal reduction from an amount, the scaled principal and the previewed debt, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:406` -> `principal-ratio-reduction`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the utilization the rate is interpolated at across its boundary values through `accrue` in simnet and assert `principal-ratio-reduction` never returns a value that breaks the invariant.
