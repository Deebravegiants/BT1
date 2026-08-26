# [M] Extra rewards are not updated in curve connector when harvestConvexRewards is called

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1554
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CurveConnector.sol#L247


# Vulnerability details

## Impact
Extra rewards are not updated in the curve connector when harvestConvexRewards is called. This leads to inaccurate calculation of the TVL.

## Proof of Concept
In the `harvestConvexRewards` function -

```solidity
    function harvestConvexRewards(address[] calldata rewardsPools) public onlyManager nonReentrant {
        for (uint256 i = 0; i < rewardsPools.length; i++) {
            IConvexBasicRewards baseRewardPool = IConvexBasicRewards(rewardsPools[i]);
            baseRewardPool.getReward(address(this), true);
        }
        _updateTokenInRegistry(CVX);
        _updateTokenInRegistry(CRV);
        emit HarvestConvexRewards(rewardsPools);
    }
```

Only CVX and CRV tokens are updated. But, when `baseRewardPool.getReward(address(this), true);` is called, the connector can also receive extra rewards. These extra rewards are not updated in the registry.

From the convex docs -

>Use baseRewardPool.getReward() or baseRewardPool.getReward( address, bool ) to claim rewards for your address or an arbitrary address.  The bool is an option to also claim extra incentive tokens (ex. snx) which is defaulted to true in the non-parametrized version.

So, these extra rewards like SNX, will not be updated in the registry. Hence, they will not be accounted for in the TVL calculation.

## Tools Used
Manual review

## Recommended Mitigation Steps
Check for these extra reward tokens and updated them in the registry using the `_updateTokenInRegistry` function.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1554_
