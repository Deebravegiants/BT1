# Q1728: process-debt-asset via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the seized zToken amount that is immediately redeemed reach `process-debt-asset` (mainnet/contracts/market/v0-4-market.clar:761) in a state where it count one deposit as backing for two simultaneous claims? Given that it caps debt at the max liquidatable USD and converts back to tokens with `mul-div-down`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:761` -> `process-debt-asset`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `process-debt-asset` caps debt at the max liquidatable USD and converts back to tokens with `mul-div-down`. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the seized zToken amount that is immediately redeemed across its boundary values through `liquidate-redeem` in simnet and assert `process-debt-asset` never returns a value that breaks the invariant.
