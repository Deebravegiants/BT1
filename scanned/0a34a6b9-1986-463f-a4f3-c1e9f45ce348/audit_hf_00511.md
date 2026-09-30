# [C] C-02 | tradeRatio Can Be Manipulated To Wipe Debt

## Summary
Severity: Critical
Contest weight: 0.2356
Dataset id: 1969
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When modifying a trade position, the output of a swap is used to calculate tradeRatio, which serves as a proxy price to determine the value of vGas. This ratio is essential for calculating PnL and setting the borrowed amounts for the new position. However, if a small (dust) amount of vGas is swapped, amountIn or amountOut for vETH may round to zero due to Uniswap’s rounding behavior, causing tradeRatio to also be zero. This allows for potential exploitation: in a long position, borrowedVEth becomes zero, effectively wiping the position's debt and creating bad debt in the system. Attack Scenario: 1. Alice opens a long position. 2. Alice decreases the position by 1 wei, setting tradeRatio to zero, which is below minPrice, creating bad debt by wiping all borrowedVEth. 3. Alice closes the position, recovering all previously deposited collateral plus additional funds, effectively stealing from the system.

## Recommendation
If the trade price is or above the min or max price for a pool, then revert.
