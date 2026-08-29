# Q4474: call-liquidate via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `call-liquidate` (mainnet/contracts/market/v0-4-market.clar:907) destroy value through a truncation the opposite operation does not restore? `call-liquidate` invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:907` -> `call-liquidate`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `call-liquidate` invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with `debt-amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
