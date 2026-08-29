# Q3086: increment via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `increment` (mainnet/contracts/market/v0-market-vault.clar:137) leave a residue that no reconciliation pass ever inspects? `increment` advances the user-id nonce, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `increment` advances the user-id nonce. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with `amount` varied, and assert that the value `increment` returns is identical in both runs; a divergence confirms the finding.
