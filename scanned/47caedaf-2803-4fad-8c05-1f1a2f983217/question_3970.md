# Q3970: interest-rate via repay: destroy value through a truncation the opposite operation 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `on-behalf-of`, naming any third-party principal, can an unprivileged attacker make `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) destroy value through a truncation the opposite operation does not restore? `interest-rate` interpolates the packed curve at the current utilization, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `repay` with `on-behalf-of`, naming any third-party principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
