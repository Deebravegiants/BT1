# Q2883: calculate-asset-notional-value via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
`calculate-asset-notional-value` (mainnet/contracts/market/v0-4-market.clar:544) normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the full batch list and its ordering, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:544` -> `calculate-asset-notional-value`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `calculate-asset-notional-value` normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calculate-asset-notional-value` touches, run `liquidate-multi` with the full batch list and its ordering, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
