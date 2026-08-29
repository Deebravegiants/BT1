# Q2320: get-notional-evaluation via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the redemption receiver reach `get-notional-evaluation` (mainnet/contracts/market/v0-4-market.clar:514) in a state where it credit one side of an accounting pair without the other? Given that it folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:514` -> `get-notional-evaluation`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the redemption receiver, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
