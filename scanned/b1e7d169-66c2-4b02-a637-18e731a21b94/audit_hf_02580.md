# [M] RedemptionVaultWIthBUIDL does not redeem

## Summary
Severity: Medium
Contest weight: 0.4275
Dataset id: 13945
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RedemptionVaultWIthBUIDL does not redeem full balance if BUIDL balance is less than 250k post transaction.
According to the specs, there should be a feature that when redeeming BUIDL tokens, it should redeem full balance if the remaining BUIDL tokens is less than RedemptionVaultWIthBUIDL does not redeem full balance if BUIDL balance is less than 250k post transaction (as 250k is the minimum). Make this 250k threshold a parameter that can be adjusted by the admin the code can be reported as issues", thus reporting this as a medium severity issue. redemption limit of 250k (according to https://www.steakhouse.financial/projects/b lackrock-buidl). Thus lack of this feature may result in lock of BUIDL tokens within the RedemptionVaultWIthBUIDL contract.
However, shares cannot be sold back unless their total value is at least $250,000, or if an exception is granted.
```solidity
function _checkAndRedeemBUIDL(address tokenOut, uint256 amountTokenOut)
internal
{
    uint256 contractBalanceTokenOut = IERC20(tokenOut).balanceOf(address(this));
    if (contractBalanceTokenOut >= amountTokenOut) return;
    uint256 buidlToRedeem = amountTokenOut - contractBalanceTokenOut;
    buidl.safeIncreaseAllowance(address(buidlRedemption), buidlToRedeem);
    buidlRedemption.redeem(buidlToRedeem);
}
```
1. Lock of BUIDL token in RedemptionVaultWIthBUIDL contract.
2. Discrepancy between spec and code.

## Recommendation
Implement such feature.
