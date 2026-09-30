# [M] Incorrect calculations of borrowingCollateral

## Summary
Severity: Medium
Contest weight: 0.5657
Dataset id: 20357
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This calculation is most likely to underflow
```solidity
uint256 borrowingCollateral = cache.borrowedAmount - cache.holdTokenBalance;
```
The cache.borrowedAmount is the calculated amount of holdTokens based on the liquidity of a position. cache.holdTokenBalance is the balance of holdTokens queried after liquidity extraction and tokens transferred to the LiquidityBorrowingManager. If any amounts of the saleToken are transferred as well, these are swapped to holdTokens and added to cache.holdTokenBalance. So in case when liquidity of a position is in the current tick range, both tokens would be transferred to the contract and saleToken would be swapped for holdToken and then added to cache.holdTokenBalance. This would make cache.holdTokenBalance > cache.borrowedAmount since cache.holdTokenBalance == cache.borrowedAmount + amount of sale token swapped and would make the tx revert due to underflow. Many positions would be unavailable to borrowers. For non-volatile positions like that which provide liquidity to stablecoin pools the DoS could last for very long period. For volatile positions that provide liquidity in a wide range this could also be for more than 1 year.

## Recommendation
The borrowedAmount should be subtracted from holdTokenBalance
```solidity
uint256 borrowingCollateral = cache.holdTokenBalance - cache.borrowedAmount;
```
