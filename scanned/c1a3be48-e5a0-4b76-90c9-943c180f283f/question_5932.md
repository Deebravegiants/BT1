# Q5932: add-user-collateral via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it adds to the collateral row with a graceful u0 default, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with `collateral-receiver`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
