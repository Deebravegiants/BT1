# [M] Possible loss of Funds

## Summary
Severity: Medium
Contest weight: 0.1458
Dataset id: 20090
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Transfers at Liquidation may silently fail, causing collateral be paid out withoud debt being paid, or liquidator not getting collateral.
in D3VaultLiquidation.sol:liquidate the caller pays the outstanding debt, and received the collateral tokens with a discount in exchange. However, the transfer of the tokens to pay the debt, as well as the transfer of the collateral Tokens are using the transferFrom function of the ERC20 interface instead of safeTransferFrom (which is used in other functions). Moreover, the return value of this function is not checked. As not all ERC20 tokens revert on a failed transfer, this could lead to a silent failure of a transfer. As the function will go on in this case this could lead to the liquidation to finish with either:
• The debt not being paid, but the collateral still paid to the caller --> Loss of protocol funds!
• The debt being repaid by the caller, but the collateral is not transferred --> Loss of user funds!
Possible loss of user or protocol funds.

## Recommendation
Usage of safeTransferFrom as in other functions of the same contract is recommended.
