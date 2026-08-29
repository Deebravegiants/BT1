# Q0279: calc-final-liquidation-amounts via liquidate: have the same quantity scaled twice by two contracts that 

## Question
`calc-final-liquidation-amounts` (mainnet/contracts/market/v0-4-market.clar:834) recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `min-collateral-expected`, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:834` -> `calc-final-liquidation-amounts`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `calc-final-liquidation-amounts` recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `calc-final-liquidation-amounts` touches, run `liquidate` with `min-collateral-expected`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
