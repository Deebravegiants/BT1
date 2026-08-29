# Q0516: mask-to-list-iter via borrow: destroy value through a truncation the opposite operation 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the order of accrual versus price resolution inside the let reach `mask-to-list-iter` (mainnet/contracts/market/v0-4-market.clar:440) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:440` -> `mask-to-list-iter`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the order of accrual versus price resolution inside the let across its boundary values through `borrow` in simnet and assert `mask-to-list-iter` never returns a value that breaks the invariant.
