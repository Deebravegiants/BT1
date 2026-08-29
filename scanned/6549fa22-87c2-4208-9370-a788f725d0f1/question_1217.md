# Q1217: receive-tokens via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the set of assets held, drive `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) — which pulls an asset from a named account — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove` call, then the attacker-shaped one with the set of assets held, and assert the attacker's net token balance change is zero or negative.
