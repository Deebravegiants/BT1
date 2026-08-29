# Q4741: send-tokens via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the seized zToken amount that is immediately redeemed, drive `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) — which pushes an asset to a caller-chosen recipient principal — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the seized zToken amount that is immediately redeemed, then read `send-tokens` state before and after in the same block and assert the two sides of the invariant are equal.
