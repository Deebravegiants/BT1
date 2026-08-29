# Q4728: merge-price via liquidate-redeem: mint shares whose backing was never received

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `merge-price` (mainnet/contracts/market/v0-4-market.clar:506) in a state where it mint shares whose backing was never received? Given that it attaches a price to an asset record by position in the fold, not by asset id, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:506` -> `merge-price`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `merge-price` attaches a price to an asset record by position in the fold, not by asset id. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the borrower targeted across its boundary values through `liquidate-redeem` in simnet and assert `merge-price` never returns a value that breaks the invariant.
