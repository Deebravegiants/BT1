# Q4341: find-collateral-amount via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the seized zToken amount that is immediately redeemed, drive `find-collateral-amount` (mainnet/contracts/market/v0-4-market.clar:609) — which returns u0 for an absent asset, making a missing row indistinguishable from a zero holding — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:609` -> `find-collateral-amount`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `find-collateral-amount` touches, run `liquidate-redeem` with the seized zToken amount that is immediately redeemed, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
