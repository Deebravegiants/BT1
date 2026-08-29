# Q4886: total-assets-preview via accrue: destroy value through a truncation the opposite operation 

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling whether an earlier call in the same block already advanced last-update, can an unprivileged attacker make `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) destroy value through a truncation the opposite operation does not restore? `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with whether an earlier call in the same block already advanced last-update varied, and assert that the value `total-assets-preview` returns is identical in both runs; a divergence confirms the finding.
