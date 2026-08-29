# Q0644: principal-ratio-reduction via deposit: destroy value through a truncation the opposite operation 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls the vault's supply and asset state at the moment of the call reach `principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:406) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it derives a principal reduction from an amount, the scaled principal and the previewed debt, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:406` -> `principal-ratio-reduction`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with the vault's supply and asset state at the moment of the call varied, and assert that the value `principal-ratio-reduction` returns is identical in both runs; a divergence confirms the finding.
