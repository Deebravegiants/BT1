# Q5887: resolve-pyth via liquidate-redeem: mint shares whose backing was never received

## Question
`resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) reads the Pyth storage record for a 32-byte ident. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the seized zToken amount that is immediately redeemed, use that to mint shares whose backing was never received, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the seized zToken amount that is immediately redeemed, then read `resolve-pyth` state before and after in the same block and assert the two sides of the invariant are equal.
