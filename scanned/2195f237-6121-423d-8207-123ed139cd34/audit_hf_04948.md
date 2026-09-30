# [M] isHoldAmountAllowed and isSubAmountAllowed logic inconsistency

## Summary
Severity: Medium
Contest weight: 0.6022
Dataset id: 22906
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HoldStableToken function checks if the given amount can be held by adding (balance.amount + balance.unsettledAmount-balance.holdAmount) and isSubAmountAllowed checks if (balance.amount - balance.holdAmount) >= amount. However, it is possible that the holdAmount is greater than the amount. In case of adding the HoldStableToken we add balance.amount and balance.unsettledAmount in isHoldAmountAllowed:
```solidity
function isHoldAmountAllowed(
    TokenBalance memory balance,
    uint256 poolLiquidityLimit,
    uint256 amount
) internal pure returns (bool) {
    if (poolLiquidityLimit == 0) {
        return balance.amount + balance.unsettledAmount - balance.holdAmount >= amount;
    } else {
        return
            CalUtils.mulRate(balance.amount + balance.unsettledAmount, poolLiquidityLimit) - balance.holdAmount >=
            amount;
    }
}
```
In case of subStableToken we check isSubAmountAllowed
```solidity
function isSubAmountAllowed(Props storage self, address stableToken, uint256 amount) public view returns (bool) {
    TokenBalance storage balance = self.stableTokenBalances[stableToken];
    if (balance.amount < amount) {
        return false;
    }
    uint256 poolLiquidityLimit = getPoolLiquidityLimit();
    if (poolLiquidityLimit == 0) {
        // this could revert due to overflow/underflow if holdAmount > amount.
    } else {
        return CalUtils.mulRate(balance.amount - amount, poolLiquidityLimit) >= balance.holdAmount;
    }
}
```
The following case could occur:
```solidity
// assume here poolLiquidityLimit=0;
balance.amount = 10e18;
balance.unsettled = 10e18;
// while adding the hold amount 12e18 , balance.amount + balance.unsettledAmount - balance.holdAmount >= amount
10e18 + 10e18 - 0 >= 12e18 // it will return true so now holdAmount=12e18
//No rebalance occur the state of token balance is same
// now we want to subtract the amount from token balance
isSubAmountAllowed would be called to check that if amount can be deducted
//return balance.amount - balance.holdAmount >= amount;
10e18 - 12e18 >= 5e18 // it will revert due to underflow/overflow
```
The Will create DoS for subStableToken calls, subStableToken function is used in different use cases like redeeming token, PnL updates and Rebalance calls.

## Recommendation
add one more check inside isSubAmountAllowed as follows:
```diff
diff --git a/elfi-perp-contracts/contracts/storage/UsdPool.sol b/elfi-perp-contracts/contracts/storage/UsdPool.sol
index 93d8aca1..dba7d141 100644
--- a/elfi-perp-contracts/contracts/storage/UsdPool.sol
+++ b/elfi-perp-contracts/contracts/storage/UsdPool.sol
@@ -240,12 +240,12 @@ library UsdPool {
function isSubAmountAllowed(Props storage self, address stableToken, uint256 amount) public view returns (bool) {
    TokenBalance storage balance = self.stableTokenBalances[stableToken];
-
    if (balance.amount < amount) {
+
    if (balance.amount < amount || balance.amount < balance.holdAmount) {
        return false;
    }
    uint256 poolLiquidityLimit = getPoolLiquidityLimit();
```
