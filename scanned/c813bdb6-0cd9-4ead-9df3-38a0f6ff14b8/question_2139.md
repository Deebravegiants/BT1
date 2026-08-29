# Q2139: oracle-last-update via collateral-remove: destroy value through a truncation the opposite operation 

## Question
`oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the `price-feeds` buffers, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `oracle-last-update` touches, run `collateral-remove` with the `price-feeds` buffers, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
