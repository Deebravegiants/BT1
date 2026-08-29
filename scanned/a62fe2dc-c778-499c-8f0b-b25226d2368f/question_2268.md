# Q2268: convert-to-assets-preview via accrue: credit one side of an accounting pair without the other

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) in a state where it credit one side of an accounting pair without the other? Given that it prices a redemption against `total-assets-preview` and `total-supply-preview`, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the utilization the rate is interpolated at across its boundary values through `accrue` in simnet and assert `convert-to-assets-preview` never returns a value that breaks the invariant.
