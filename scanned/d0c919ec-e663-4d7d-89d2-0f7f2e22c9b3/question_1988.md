# Q1988: total-assets-preview via deposit: credit one side of an accounting pair without the other

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls whether the vault is at a zero-supply or zero-asset edge reach `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) in a state where it credit one side of an accounting pair without the other? Given that it re-derives a FORWARD index inside calls that have already accrued, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with whether the vault is at a zero-supply or zero-asset edge varied, and assert that the value `total-assets-preview` returns is identical in both runs; a divergence confirms the finding.
