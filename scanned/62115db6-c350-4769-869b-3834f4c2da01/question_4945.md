# Q4945: interest-rate via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling remaining zToken collateral whose price moves with the redeem, drive `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) — which interpolates the packed curve at the current utilization — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, then read `interest-rate` state before and after in the same block and assert the two sides of the invariant are equal.
