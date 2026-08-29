# Q3626: convert-to-shares-preview via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling the vault's supply and asset state at the moment of the call, can an unprivileged attacker make `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) leave a residue that no reconciliation pass ever inspects? `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with the vault's supply and asset state at the moment of the call varied, and assert that the value `convert-to-shares-preview` returns is identical in both runs; a divergence confirms the finding.
