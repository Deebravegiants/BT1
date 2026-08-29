# Q3387: calc-cumulative-debt via transfer: count one deposit as backing for two simultaneous claims

## Question
`calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) multiplies scaled principal by an index. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing the timing relative to a pledge or a liquidation, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calc-cumulative-debt` touches, run `transfer` with the timing relative to a pledge or a liquidation, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
