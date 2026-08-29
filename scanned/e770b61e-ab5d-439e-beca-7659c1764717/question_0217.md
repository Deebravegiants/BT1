# Q0217: remove-user-collateral via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the seized zToken amount that is immediately redeemed, drive `remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) — which asserts sufficiency then `map-delete`s only on an exact zero — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the seized zToken amount that is immediately redeemed, then read `remove-user-collateral` state before and after in the same block and assert the two sides of the invariant are equal.
