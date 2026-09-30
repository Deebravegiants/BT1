# [M] Unauthorized rewardTokens in _marketWeightsByToken

## Summary
Severity: Medium
Contest weight: 0.5970
Dataset id: 9043
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _marketWeightsByToken variable is used in the RewardDistributor::_updateMarketRewards function to assign rewards to a market based on the weight assigned to that market:
File: RewardDistributor.sol
```solidity
function _updateMarketRewards(address market) internal override {
    uint256 newRewards = getInflationRate(token).mulDiv(_marketWeightsByToken[token][market], MAX_BASIS_POINTS)
        .mulDiv(deltaTime, 365 days).div(_totalLiquidityPerMarket[market]);
    if (newRewards != 0) {
        _cumulativeRewardPerLpToken[token][market] += newRewards;
        emit RewardAccruedToMarket(market, token, newRewards);
    }
}
```
The issue arises when the rewardToken is removed using the RewardDistributor::removeRewardToken function and later re-added using the RewardDistributor::addRewardToken function. Consider the following scenario:
1. The rewardTokenA is allocated 100% to the stakedToken1 market. Therefore, _marketWeightsByToken[rewardTokenA][stakedToken1]=100%.
2. The rewardTokenA is removed using the RewardDistributor::removeRewardToken function. At this point _marketWeightsByToken[rewardTokenA][stakedToken1] is not cleared.
3. The rewardTokenA is added back using the RewardDistributor::addRewardToken function, but it is assigned to a different market, so rewardTokenA now distributes 100% to the stakedToken2 market, hence _marketWeightsByToken[rewardTokenA][stakedToken2]=100%.
4. Then, a malicious user calls updatePosition using the stakedToken1 market, triggering RewardDistributor::_updateMarketRewards(stakedToken1). Since _marketWeightsByToken[rewardTokenA][stakedToken1] was never reset to zero, rewards are assigned to this market (stakedToken1), even though rewardTokenA is no longer allocated to it.
The market stakedToken1 will receive unauthorized rewards even when rewardTokenA distributes 100% to the stakedToken2 market in step3, not to the stakedToken1 market.

## Recommendation
When removing a rewardToken, ensure that the associated _marketWeightsByToken is also cleared.
```solidity
function removeRewardToken(address _rewardToken) external onlyRole(GOVERNANCE) {
    // Update rewards for all markets before removal
    uint256 numMarkets = _rewardInfoByToken[_rewardToken].marketAddresses
    for (uint256 i; i < numMarkets;) {
        _updateMarketRewards(_rewardInfoByToken[_rewardToken].marketAddresses[i]);
        unchecked {
            ++i; // saves 63 gas per iteration
        }
    }
    delete _marketWeightsByToken[_rewardToken][_rewardInfoByToken[_rewardToken
```
