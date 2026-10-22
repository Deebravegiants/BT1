# [M]  Incorrect accounting for yieldBoxShares in SGLLiquidation results in wrongly read values

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1349
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L29-L65


# Vulnerability details

## Impact

Wrong accounting is done for yieldBoxShares while liquidating through the SGLLiquidation#liquidate function. This results in wrong values being read from the yieldBoxShares() function in the Singularity market. This might result in unintended behavior from other contracts which read from this function.

## Proof of Concept

When a user adds collateral to the singularity market through SGLCollateral#addCollateral, the SGLLendingCommon#_addTokens function is called as we can see in the following code lines: 

1. https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLendingCommon.sol#L16-L38

2. https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLCommon.sol#L174-L194

As we can see here, yieldBoxShares is updated to include the number of shares supplied while supplying collateral. Therefore, if the user borrows an amount, and is unable to pay and hence is to be liquidated, the SGLLiquidation#liquidate function is called on them. This should update the user’s yieldBoxShares to a new value, but they do not do this. Both the _closedLiquidation and _orderBookLiquidation methods do not update yieldBoxShares. 

This results in wrong values stored as yieldBoxShares owned by a particular user, and hence when another contract calls Singularity#yieldBoxShares, the wrong value is supplied. 

## Tools Used

Manual Review

## Recommended Mitigation Steps 

Update yieldBoxShares when liquidating. 




## Assessed type

Other
