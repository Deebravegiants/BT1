# Q2475: resolve-dia via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
`resolve-dia` (mainnet/contracts/market/v0-4-market.clar:326) derives a (string-ascii 32) key from a (buff 32) ident. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `min-shares` (the only slippage bound on the deposit leg), use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:326` -> `resolve-dia`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-dia` touches, run `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
