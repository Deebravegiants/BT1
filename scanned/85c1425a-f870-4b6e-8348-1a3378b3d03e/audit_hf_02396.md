# [M] Possibly Inaccurate Rate Calculation in RewardDistributor

## Summary
Severity: Medium
Contest weight: 0.3744
Dataset id: 12933
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function fetchRewardManual() external {
    if (ChainUtils.getTime() < lastRewardFetchTime + rewardFetchInterval) revert("RewardDistributor: not time yet");
    uint256 _rewardAmount = IStableVault(vault).claimReward(rewardToken(), 0);
    lastRewardFetchTime = ChainUtils.getTime();
    uint256 _tokensPerInterval = _rewardAmount / rewardFetchInterval;
    _setTokensPerInterval(_tokensPerInterval);
}
```

## Recommendation
Revise the above reward-disseminating routine to compute and use the accurate rate for reward token dissemination.
