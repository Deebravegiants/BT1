# Q0027: normalize-pyth via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
`normalize-pyth` (mainnet/contracts/market/v0-4-market.clar:297) computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the `ft` trait principal, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:297` -> `normalize-pyth`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `normalize-pyth` computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `normalize-pyth` touches, run `collateral-remove` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
