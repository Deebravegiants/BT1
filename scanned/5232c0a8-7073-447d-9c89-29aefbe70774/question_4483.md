# Q4483: total-supply-preview via accrue: credit one side of an accounting pair without the other

## Question
`total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the utilization the rate is interpolated at, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with the utilization the rate is interpolated at, then read `total-supply-preview` state before and after in the same block and assert the two sides of the invariant are equal.
