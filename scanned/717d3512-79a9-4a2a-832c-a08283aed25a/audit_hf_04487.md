# [C] C-07 | Undercollateralized Positions Can Be Created

## Summary
Severity: Critical
Contest weight: 0.2921
Dataset id: 22050
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In this line, if loanAmount0 > maxAmount0, then the excess loanAmount0 is not considered in the collateralization check: uint256 availableAmount0 = maxAmount0 > loanAmount0 ? maxAmount0 - loanAmount0 : 0; The loanAmount0 entered into collateralRequirementAtMinTick is loanAmount0 - tokensOwed0. Here is a sequence which leads to a state where loanAmount0 > maxAmount0: 1. Create a liquidity position when the current tick is below tickLower, so the loaned amount is 100% token0 2. Swap so the position is liquidity entirely token1 3. Remove most of the liquidity via decreaseLiquidityPosition. Since the LP is now 100% token1, all the claimed tokens from decreaseLiquidityPosition would be token1 (except for a tiny amount of LP fees). DecreaseLiquidityPosition reduced the maxAmount0, while loanAmount0 is still the amount0 required to create the initial position, so maxAmount0 > loanAmount0. Now it is true that decreasing a liquidity position should make the collateral requirements lower, but this is already accounted for in tokensOwed0 tokensOwed1 being deducted from loan amounts. 1. Create a position that requires loaning token0 2. Swap so the position is entirely token1 3. decreaseLiquidityPosition. All the claimed tokens from decreaseLiquidityPosition would be token1 (except for a tiny amount of LP fees).

## Recommendation
Consider converting loanAmount0 to the corresponding ETH value and incorporating it into the collateral calculation rather than subtracting it from maxAmount0.
