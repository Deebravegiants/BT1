# [C] Profit and loss distribution mechanism is not working

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Liquidity providers should deposit DAI and receive DAIx in return; the initial rate of DAI to DAIx is 1. If claims are happening, the price of DAIx should decrease, and the loss should be distributed proportionally across the liquidity providers. If the policy is bought, the DAIx price should increase. Currently, it seems like the `getDAIToDAIxRatio` will always be zero because it's based on the `totalLiquidity` to the `totalSupply()` ratio. While the `totalSupply()` remains correct, the `totalLiquidity` is only modified when adding/removing liquidity. The `totalLiquidity` should represent the amount of DAI in the smart contract,  which is the added liquidity + premium - claims. But the claims and premiums are not changing the `totalLiquidity` value.

That error may also lead to the deficit of funds during withdrawals or claims.

#### Recommendation

Properly keep track of the `totalLiquidity`.
