# Q4277: user-safe-mask via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the `ft` trait principal, drive `user-safe-mask` (mainnet/contracts/market/v0-4-market.clar:428) — which ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:428` -> `user-safe-mask`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove` call, then the attacker-shaped one with the `ft` trait principal, and assert the attacker's net token balance change is zero or negative.
