# Q2917: accrue-user-collateral via accrue: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling whether an earlier call in the same block already advanced last-update, drive `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) — which accrues only rows that `is-ztoken` recognises, skipping everything else — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with whether an earlier call in the same block already advanced last-update, then read `accrue-user-collateral` state before and after in the same block and assert the two sides of the invariant are equal.
