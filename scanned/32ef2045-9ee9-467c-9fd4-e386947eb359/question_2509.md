# Q2509: ubalance via accrue: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling whether an earlier call in the same block already advanced last-update, drive `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) — which reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with whether an earlier call in the same block already advanced last-update, then read `ubalance` state before and after in the same block and assert the two sides of the invariant are equal.
