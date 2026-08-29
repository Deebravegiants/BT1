# Q3969: merge-price via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling the `ft` trait principal deciding which vault is routed to, drive `merge-price` (mainnet/contracts/market/v0-4-market.clar:506) — which attaches a price to an asset record by position in the fold, not by asset id — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:506` -> `merge-price`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `merge-price` attaches a price to an asset record by position in the fold, not by asset id. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `merge-price` touches, run `supply-collateral-add` with the `ft` trait principal deciding which vault is routed to, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
