# Q3302: total-assets via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) leave a residue that no reconciliation pass ever inspects? `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with `amount` varied, and assert that the value `total-assets` returns is identical in both runs; a divergence confirms the finding.
