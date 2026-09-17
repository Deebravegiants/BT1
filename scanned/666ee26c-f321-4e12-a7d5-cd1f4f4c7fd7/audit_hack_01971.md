# [H] 6.19 liquidity Gets Overwritten in the Loop

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The following loop in LStrategy._rebalanceUniV3Liquidity updates the liquidity for vault tokens
in a loop:

```
for (uint256 i = 0; i < 2; i++) {
...
liquidity = uint128(
FullMath.mulDiv(
availableBalances[i],
shouldDepositTokenAmountsD[i] - shouldWithdrawTokenAmountsD[i],
DENOMINATOR
)
);
}
```
The final value of liquidity after the loop exists should be the minimum value calculated in each
iteration, however, the loop above overwrites the liquidity on each iteration without performing any
check.

Code corrected:

In Version 2 the potentialLiquidity is computed on each iteration of the loop and it is compared
with liquidity, hence liquidity can only decrease in the loop:


```
liquidity = potentialLiquidity < liquidity? potentialLiquidity : liquidity;
```
