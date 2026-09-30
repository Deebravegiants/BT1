# [M] addStakedToken() can be griefed

## Summary
Severity: Medium
Contest weight: 0.5953
Dataset id: 9051
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a StakedToken is added to the SafetyModule via addStakedToken(), it will call initMarketStartTime(StakedToken) to set _timeOfLastCumRewardUpdate[StakedToken] = block.timestamp. If _timeOfLastCumRewardUpdate was already set for that StakedToken, a check will cause a revert to ensure that the start time has not been initialized.
```solidity
function initMarketStartTime(address _market) external onlySafetyModule {
    // @audit When this function is called by addStakedToken(), this check will revert
    // if start time has already been initialized
    if (_timeOfLastCumRewardUpdate[_market] != 0) {
        revert RewardDistributor_AlreadyInitializedStartTime(_market);
    }
    _timeOfLastCumRewardUpdate[_market] = block.timestamp;
}
```
However, an attacker can exploit this check to cause addStakedToken() to fail by performing a StakedToken.stake() with just 1 wei followed by a registerPositions([StakedToken]). This will indirectly call _updateMarketRewards(StakedToken), which will then set _timeOfLastCumRewardUpdate[StakedToken] = block.timestamp, as it has not been initialized yet.
Now that _timeOfLastCumRewardUpdate is initialized for the StakedToken, it will cause subsequent addStakedToken() for that particular StakedToken to revert and fail.
```solidity
function _updateMarketRewards(address market) internal override {
    uint256 numTokens = rewardTokens.length;
    uint256 deltaTime = block.timestamp - _timeOfLastCumRewardUpdate[mark
    if (deltaTime == 0 || numTokens == 0) return;
    (deltaTime == block.timestamp || _totalLiquidityPerMarket[market] == 0) {
        // Either the market has never been updated or it has no liquidity,
        // so just initialize the timeOfLastCumRewardUpdate and return
        // @audit This can be triggered by attacker via stake() and registerPositions(),
        // before the StakedToken (market) is added to SafetyModule
        // to cause addStakedToken() to revert.
        _timeOfLastCumRewardUpdate[market] = block.timestamp;
        return;
    }
}
```

## Recommendation
Remove registerPositions() for SMRewardDistributor since it is not required.
Alternatively, in SMRewardDistributor._registerPosition(), verify that the StakedToken has been added to SafetyModule using the check safetyModule.getStakedTokenIdx(market).
