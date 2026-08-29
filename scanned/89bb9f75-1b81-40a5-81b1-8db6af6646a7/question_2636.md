# Q2636: unpack-u16 via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `recipient` reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it credit one side of an accounting pair without the other? Given that it unpacks eight u16 curve fields from one packed word, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `recipient` varied, and assert that the value `unpack-u16` returns is identical in both runs; a divergence confirms the finding.
