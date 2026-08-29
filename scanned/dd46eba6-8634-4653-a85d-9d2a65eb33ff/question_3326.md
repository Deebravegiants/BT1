# Q3326: add-user-collateral via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) leave a residue that no reconciliation pass ever inspects? `add-user-collateral` adds to the collateral row with a graceful u0 default, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with `amount` varied, and assert that the value `add-user-collateral` returns is identical in both runs; a divergence confirms the finding.
