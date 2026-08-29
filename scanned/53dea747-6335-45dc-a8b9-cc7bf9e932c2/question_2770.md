# Q2770: merge-price via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the borrower targeted, can an unprivileged attacker make `merge-price` (mainnet/contracts/market/v0-4-market.clar:506) have the same quantity scaled twice by two contracts that round differently? `merge-price` attaches a price to an asset record by position in the fold, not by asset id, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:506` -> `merge-price`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `merge-price` attaches a price to an asset record by position in the fold, not by asset id. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the borrower targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
