# Q3603: get-cached-indexes via redeem: count one deposit as backing for two simultaneous claims

## Question
`get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing `amount` of shares burned, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `get-cached-indexes` touches, run `redeem` with `amount` of shares burned, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
