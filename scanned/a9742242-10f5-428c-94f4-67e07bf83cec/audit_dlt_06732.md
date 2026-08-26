# [M] dailyDebtIncreaseLimitLeft is not updated in liquidate().

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-revert-lend
Published: 2024-03-13
Source: https://github.com/code-423n4/2024-03-revert-lend-findings/issues/140
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-03-revert-lend/blob/435b054f9ad2404173f36f0f74a5096c894b12b7/src/V3Vault.sol#L685-L757


# Vulnerability details

## Impact
On days with a significant number of liquidated positions, particularly when the asset quantity is substantial, there will be an excess of assets available in the vault that cannot be borrowed, thereby causing a drastic decrease in the utilization rate.

This also contradicts what was stated in the ```repay()``` function, which asserts that repaid amounts should be borrowed again. Liquidation is also a form of repayment.
``` solidity
 // when amounts are repayed - they maybe borrowed again
        dailyDebtIncreaseLimitLeft += assets; 
```

## Proof of Concept
```dailyDebyIncreaseLimitLeft``` was not increamented in ```liquidate()```. **[here](https://github.com/code-423n4/2024-03-revert-lend/blob/435b054f9ad2404173f36f0f74a5096c894b12b7/src/V3Vault.sol#L685-L757)**

## Tools Used
Manual review.

## Recommended Mitigation Steps
Include ```dailyDebyIncreaseLimitLeft``` increment in ```liquidate()```.
``` solidity
dailyDebtIncreaseLimitLeft += state.liquidatorCost;
```


## Assessed type

Context
