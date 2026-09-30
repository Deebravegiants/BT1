# [M] TradableStaking: Users cannot unstake all their shares

## Summary
Severity: Medium
Contest weight: 0.5404
Dataset id: 16146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _unstake function of the TradableStaking contract has the following code:
```solidity
require(userShares < _stakes.shares, "!insufficient-shares");
bool isFullRedeem = userShares >= uint256(_stakes.shares);
if (isFullRedeem) {
    userShares = uint256(_stakes.shares);
}
```
Here, there are conflicting inequalities. Since userShares must be smaller than _stakes.shares, it can never be bigger or equal to _stakes.shares. The requirement also stops users from unstaking all their shares.

## Recommendation
It should probably be:
```solidity
require(userShares <= _stakes.shares, "!insufficient-shares");
bool isFullRedeem = userShares == uint256(_stakes.shares);
```
Note that the if is not necessary.
