# Q2652: convert-to-assets-preview via transfer: credit one side of an accounting pair without the other

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls `amount` reach `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) in a state where it credit one side of an accounting pair without the other? Given that it prices a redemption against `total-assets-preview` and `total-supply-preview`, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `transfer` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `transfer` in simnet and assert `convert-to-assets-preview` never returns a value that breaks the invariant.
