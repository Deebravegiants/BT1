# [M] _calculateMaxBorrowCollateral

## Summary
Severity: Medium
Contest weight: 0.4275
Dataset id: 1752
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
When calculating the amount to repay, _calculateMaxBorrowCollateral incorrectly applies unutilizedLeveragePercentage when calculating netRepayLimit. The result is that if the borrowBalance ever exceeds liquidationThreshold*(1-unutilizedLeveragePercentage) then all attempts to repay will revert. This is nearly identical to the valid issue In MorphoLeverageStrategyExtension.sol:L1124 the borrow limit is reduced by unutilized LeveragePercentage which will cause L1134 to underflow and revert.
Internal pre-conditions
unutilizedLeveragePercentage must be a nonzero value. For context this is nonzero for every existing leveraged token currently deployed by Index Coop.
External pre-conditions
The underlying collateral value decreases rapidly in price pushing the set towards liquidation
Attack Path
1. The price of the underlying collateral decreases rapidly causing liquidationThreshold to drop
2. borrowBalance exceeds liquidationThreshold*(1-unutilizedLeveragPercentage)
3. Calls to MorphoLeverageStrategyExtension#ripcord will revert due to underflow
4. Set token is liquidated
Set token suffers losses due to liquidation fee. For most Morpho markets this is at least 5%. Due to the leveraged nature of the set the loss will be multiplicative. This means a 3x leverage token will lose 15% NAV (5% * 3), 5x leverage will lose 25% NAV (5% * 5), etc.
```

## Recommendation
Don't adjust the max value by unutilizedLeveragPercentage when deleveraging
