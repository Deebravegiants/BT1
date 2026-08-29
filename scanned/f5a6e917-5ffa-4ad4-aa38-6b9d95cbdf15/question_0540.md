# Q0540: resolve-price-feed via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the borrower targeted across its boundary values through `liquidate-redeem` in simnet and assert `resolve-price-feed` never returns a value that breaks the invariant.
