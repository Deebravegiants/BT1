# Q2458: linear-interpolate via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the set of assets held, can an unprivileged attacker make `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) have the same quantity scaled twice by two contracts that round differently? `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove` with the set of assets held, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
