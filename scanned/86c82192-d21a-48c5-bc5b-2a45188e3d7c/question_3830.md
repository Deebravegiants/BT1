# Q3830: send-underlying via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) leave a residue that no reconciliation pass ever inspects? `send-underlying` pushes the underlying under an `as-contract?` post-condition scope, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with `amount` varied, and assert that the value `send-underlying` returns is identical in both runs; a divergence confirms the finding.
