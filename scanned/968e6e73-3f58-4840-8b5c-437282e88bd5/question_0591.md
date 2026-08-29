# Q0591: active via liquidate: have the same quantity scaled twice by two contracts that 

## Question
`active` (mainnet/contracts/registry/v0-egroup.clar:238) lists candidate bucket masks at or above a population. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `min-collateral-expected`, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:238` -> `active`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `active` lists candidate bucket masks at or above a population. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `active` touches, run `liquidate` with `min-collateral-expected`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
