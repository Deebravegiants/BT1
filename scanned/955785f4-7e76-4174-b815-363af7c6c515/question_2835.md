# Q2835: filter-u128 via liquidate: destroy value through a truncation the opposite operation 

## Question
`filter-u128` (mainnet/contracts/registry/v0-egroup.clar:97) filters a 128-entry bucket list. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing which collateral and debt asset pair is targeted, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:97` -> `filter-u128`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `filter-u128` filters a 128-entry bucket list. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `filter-u128` touches, run `liquidate` with which collateral and debt asset pair is targeted, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
