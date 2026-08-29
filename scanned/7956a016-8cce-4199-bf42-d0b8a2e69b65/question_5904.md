# Q5904: total-assets-preview via deposit: have the same quantity scaled twice by two contracts that 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls whether the vault is at a zero-supply or zero-asset edge reach `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it re-derives a FORWARD index inside calls that have already accrued, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `deposit` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz whether the vault is at a zero-supply or zero-asset edge across its boundary values through `deposit` in simnet and assert `total-assets-preview` never returns a value that breaks the invariant.
