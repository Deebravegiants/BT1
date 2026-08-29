# Q2743: normalize-pyth via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
`normalize-pyth` (mainnet/contracts/market/v0-4-market.clar:297) computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the seized zToken amount that is immediately redeemed, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:297` -> `normalize-pyth`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `normalize-pyth` computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the seized zToken amount that is immediately redeemed, then read `normalize-pyth` state before and after in the same block and assert the two sides of the invariant are equal.
