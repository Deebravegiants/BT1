# Q2390: convert-to-assets-preview via deposit: have the same quantity scaled twice by two contracts that 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `min-out`, can an unprivileged attacker make `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) have the same quantity scaled twice by two contracts that round differently? `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `deposit` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `min-out` varied, and assert that the value `convert-to-assets-preview` returns is identical in both runs; a divergence confirms the finding.
