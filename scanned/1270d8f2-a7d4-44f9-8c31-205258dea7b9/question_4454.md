# Q4454: debt-preview via deposit: destroy value through a truncation the opposite operation 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `recipient`, including a contract principal, can an unprivileged attacker make `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) destroy value through a truncation the opposite operation does not restore? `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `recipient`, including a contract principal varied, and assert that the value `debt-preview` returns is identical in both runs; a divergence confirms the finding.
