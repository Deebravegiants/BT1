# Q2391: get-cached-indexes via liquidate: destroy value through a truncation the opposite operation 

## Question
`get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing which collateral and debt asset pair is targeted, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `get-cached-indexes` touches, run `liquidate` with which collateral and debt asset pair is targeted, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
