# Q1339: next-index via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
`next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing remaining zToken collateral whose price moves with the redeem, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, then read `next-index` state before and after in the same block and assert the two sides of the invariant are equal.
