# Q0955: receive-underlying via transfer: have the same quantity scaled twice by two contracts that 

## Question
`receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) pulls the underlying from a named account. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing the destination principal, including the market, the market-vault or the treasury, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with the destination principal, including the market, the market-vault or the treasury, then read `receive-underlying` state before and after in the same block and assert the two sides of the invariant are equal.
