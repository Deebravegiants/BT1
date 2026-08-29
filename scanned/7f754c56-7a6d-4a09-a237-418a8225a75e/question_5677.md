# Q5677: check-confidence via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the order of accrual versus price resolution inside the let, drive `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) — which compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the order of accrual versus price resolution inside the let, then read `check-confidence` state before and after in the same block and assert the two sides of the invariant are equal.
