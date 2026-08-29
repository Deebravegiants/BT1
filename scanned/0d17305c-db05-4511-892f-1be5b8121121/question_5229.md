# Q5229: interpolate-rate via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the redemption receiver, drive `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) — which interpolates between packed u16 curve points — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `interpolate-rate` touches, run `liquidate-redeem` with the redemption receiver, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
