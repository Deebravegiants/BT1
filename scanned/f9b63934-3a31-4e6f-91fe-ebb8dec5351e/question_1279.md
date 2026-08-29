# Q1279: interpolate-rate via redeem: leave a residue that no reconciliation pass ever inspects

## Question
`interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) interpolates between packed u16 curve points. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing the gap between the `assets` var and the real balance, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `redeem` with the gap between the `assets` var and the real balance, then read `interpolate-rate` state before and after in the same block and assert the two sides of the invariant are equal.
