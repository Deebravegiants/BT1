# [M] BigBang liquidation share is not distributed 100%

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1139
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/markets/bigBang/BigBang.sol#L576-L626
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/markets/bigBang/BigBang.sol#L639-L650


# Vulnerability details

## Impact
When a BigBang liquidation occurs, both the liquidate caller and the protocol is awarded with fees. When a liquidation occurs, BigBang._liquidateUser is called and the rewards are distributed in the `_extractLiquidationFees ` function. Unfortunately, there is no check that the feeShare and callerShare within `_extractLiquidationFees ` will cover 100% of the extraShare collected from the liquidation. 

This causes the possibility for not all extra shares to be distributed to both the liquidation caller or the fee holder.

This occurs because the _getCallerReward in certain circumstances will return a value that is less than `1e6 - protocolFee`. For example, if the borrowed >= maxTVLInAsset, then the minLiquidatorReward will be returned, which is `1e3`. 

## Proof of Concept

### Relevant code

```solidity
// From Market.sol
//
// _getCallerReward returns a percentage (basis points) of how much funds go to the caller.
//
function _getCallerReward(
    uint256 borrowed,
    uint256 startTVLInAsset,
    uint256 maxTVLInAsset
) internal view returns (uint256) {
    if (borrowed == 0) return 0;
    if (startTVLInAsset == 0) return 0;

    if (borrowed < startTVLInAsset) return 0;
    if (borrowed >= maxTVLInAsset) return minLiquidatorReward; // If borrowed exceeded maxTVLInAsset, then minLiquidatorReward will be returned as the callerReward. In Market.sol, this is 1e3 or 1%.

    uint256 rewardPercentage = ((borrowed - startTVLInAsset) *
        FEE_PRECISION) / (maxTVLInAsset - startTVLInAsset);

    int256 diff = int256(minLiquidatorReward) - int256(maxLiquidatorReward);
    int256 reward = (diff * int256(rewardPercentage)) /
        int256(FEE_PRECISION) +
        int256(maxLiquidatorReward);

    return uint256(reward);
}

// From BigBang.sol
function _extractLiquidationFees(
    uint256 returnedShare,
    uint256 borrowShare,
    uint256 callerReward // AUDIT: this value comes from the result of _getCallerReward()
) private returns (uint256 feeShare, uint256 callerShare) {
    uint256 extraShare = returnedShare - borrowShare;
    feeShare = (extraShare * protocolFee) / FEE_PRECISION; // x% of profit goes to fee.
    callerShare = (extraShare * callerReward) / FEE_PRECISION; //  y%  of profit goes to caller.

    // AUDIT: There is no check here that the callerShare and feeShare equal extraShare. This introduces cases where not all liquidation rewards are distributed properly

    yieldBox.transfer(address(this), penrose.feeTo(), assetId, feeShare);
    yieldBox.transfer(address(this), msg.sender, assetId, callerShare);
}
```

### Steps to Reproduce

1. A liquidator discovers a loan where the borrowed amount is greater than or equal to maxTVLInAsset. 
2. A liquidator liquidates the loan. Because the borrowed amount is greater than or equal to maxTVLInAsset, the _getCallerReward will return minLiquidatorReward which is equal to 1e3.
3. The callerReward is passed into _extractLiquidationFees, which is used to collect the callerShare. 
4. Within _extractLiquidationFees, the callerReward equals 1e3 and protocolFee by default is 1e4. This equals 1.1e4 which is below 1e6 which represents 100%. This results in 98.9% of the extra shares not sent to either the liquidation caller nor the fee owner.

## Tools Used

Manual inspection

## Recommended Mitigation Steps

The BigBang contract should validate that the feeShare and extraShare equals 1e6. Any leftover shares can either be sent to the liquidation caller or added to the collected fees.

## Anything Else We Should Know

Leoni confirmed with us that within BigBang._extractLiquidationFees Tapioca anticipate that 100% of the returned shares are distributed between the liquidation caller and the address that stores the liquidation fees.


## Assessed type

Math
