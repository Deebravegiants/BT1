# Q1951: receive-underlying via accrue: leave a residue that no reconciliation pass ever inspects

## Question
`receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) pulls the underlying from a named account. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the utilization the rate is interpolated at, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `accrue` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with the utilization the rate is interpolated at, then read `receive-underlying` state before and after in the same block and assert the two sides of the invariant are equal.
