# Q2451: convert-to-scaled-debt via liquidate: destroy value through a truncation the opposite operation 

## Question
`convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) scales a token amount by the cached borrow index, rounding up on the borrow path. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing which collateral and debt asset pair is targeted, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `convert-to-scaled-debt` touches, run `liquidate` with which collateral and debt asset pair is targeted, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
