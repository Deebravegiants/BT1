# Q4399: total-assets-preview via transfer: credit one side of an accounting pair without the other

## Question
`total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) re-derives a FORWARD index inside calls that have already accrued. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing `amount`, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `transfer` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with `amount`, then read `total-assets-preview` state before and after in the same block and assert the two sides of the invariant are equal.
