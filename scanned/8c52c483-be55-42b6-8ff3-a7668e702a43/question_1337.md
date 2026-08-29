# Q1337: get-cached-indexes via liquidate-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the redemption receiver, drive `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) — which reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `liquidate-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the redemption receiver, and assert the attacker's net token balance change is zero or negative.
