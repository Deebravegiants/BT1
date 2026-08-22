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

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1139_
