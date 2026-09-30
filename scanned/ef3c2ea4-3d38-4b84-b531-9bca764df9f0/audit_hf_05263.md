# [M] In the RedemptionManager::executeTwoStepRedemption function

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23472
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: In the RedemptionManager::executeTwoStepRedemption function, the following call is made:
```solidity
params.liquidityProvider.supplyTo(contractAddress, params.liquidityTokenAmount, params.minOutputAmount);
```
Here, params.minOutputAmount is used as the minimum expected return from the liquidity provider. However, this
value does not account for any fee deductions that are applied later in the function.
Immediately after the supplyTo call, the contract performs a slippage protection check:
```solidity
uint256 offRampBalance = params.liquidityProvider.liquidityToken().balanceOf(contractAddress);
uint256 fee = _getFee(params.feeManager, offRampBalance);
if (offRampBalance - fee < params.minOutputAmount) {
    revert Errors.SlippageControlError();
}
```
If the liquidity provider returns exactly minOutputAmount, then the deduction of the fee from that amount will cause
offRampBalance - fee to fall below minOutputAmount, resulting in a slippage error—even though the liquidity
provider met the minimum requirement.
The issue is not with the slippage check itself, which is correctly accounting for the fee. The problem is that the
minOutputAmount passed to supplyTo should also include the fee, to ensure consistency with the later slippage
check.

## Recommendation
Recommended Mitigation: Update the call to supplyTo to include the expected fee in the minOutputAmount
parameter. For example:
```solidity
uint256 expectedFee = _getFee(params.feeManager, params.minOutputAmount);
params.liquidityProvider.supplyTo(
    contractAddress,
    params.liquidityTokenAmount,
    params.minOutputAmount + expectedFee
);
```
This ensures that the post-fee amount meets the expected minimum and aligns with the logic in the slippage
protection check.
