# Q5164: resolve-pyth via call-ststx-ratio: record a repayment larger than the value actually delivere

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls the block and transaction position at which the external ratio is fetched reach `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) in a state where it record a repayment larger than the value actually delivered? Given that it reads the Pyth storage record for a 32-byte ident, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `call-ststx-ratio` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
