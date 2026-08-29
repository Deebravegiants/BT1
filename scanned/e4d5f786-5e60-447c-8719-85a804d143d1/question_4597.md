# Q4597: interpolate-rate via accrue: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the utilization the rate is interpolated at, drive `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) — which interpolates between packed u16 curve points — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `accrue` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with the utilization the rate is interpolated at, then read `interpolate-rate` state before and after in the same block and assert the two sides of the invariant are equal.
