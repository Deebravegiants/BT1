# Q2928: total-assets-preview via accrue: credit one side of an accounting pair without the other

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) in a state where it credit one side of an accounting pair without the other? Given that it re-derives a FORWARD index inside calls that have already accrued, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the utilization the rate is interpolated at across its boundary values through `accrue` in simnet and assert `total-assets-preview` never returns a value that breaks the invariant.
