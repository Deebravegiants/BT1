# Q4298: next-index via accrue: destroy value through a truncation the opposite operation 

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling whether an earlier call in the same block already advanced last-update, can an unprivileged attacker make `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) destroy value through a truncation the opposite operation does not restore? `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with whether an earlier call in the same block already advanced last-update varied, and assert that the value `next-index` returns is identical in both runs; a divergence confirms the finding.
