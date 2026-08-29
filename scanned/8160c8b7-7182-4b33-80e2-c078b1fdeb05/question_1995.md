# Q1995: total-supply-preview via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
`total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `min-shares` (the only slippage bound on the deposit leg), use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `total-supply-preview` touches, run `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
