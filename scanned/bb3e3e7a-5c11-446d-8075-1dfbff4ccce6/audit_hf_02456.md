# [M] Incorrect Calculation of lpPercent in SynthChef

## Summary
Severity: Medium
Contest weight: 0.4252
Dataset id: 13161
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function poolRewardsPerSec(
    uint256 _pid
) external Public view validatePoolByPid(_pid) returns (
    address[] memory addresses,
    string[] memory symbols,
    uint256[] memory decimals,
    uint256[] memory rewardsPerSec
) {
    PoolInfo storage pool = poolInfo[_pid];
    addresses = new address[](pool.rewarders.length + 1);
    symbols = new string[](pool.rewarders.length + 1);
    decimals = new uint256[](pool.rewarders.length + 1);
    rewardsPerSec = new uint256[](pool.rewarders.length + 1);
    addresses[0] = address(synth);
    symbols[0] = IBoringERC20(synth).safeSymbol();
    decimals[0] = IBoringERC20(synth).safeDecimals();
    uint256 total = 1000;
    uint256 lpPercent = total - marketingPercent;
    rewardsPerSec[0] = (pool.allocPoint * synthPerSec * lpPercent) / totalAllocPoint / total;
    for (uint256 rewarderId = 0; rewarderId < pool.rewarders.length; ++rewarderId) {
        addresses[rewarderId + 1] = address(pool.rewarders[rewarderId].rewardToken());
        symbols[rewarderId + 1] = IBoringERC20(pool.rewarders[rewarderId].rewardToken()).safeSymbol();
        decimals[rewarderId + 1] = IBoringERC20(pool.rewarders[rewarderId].rewardToken()).safeDecimals();
        rewardsPerSec[rewarderId + 1] = pool.rewarders[rewarderId].poolRewardsPerSec(_pid);
    }
    Public
}
```

## Recommendation
Revise the above two routines to properly compute the pending rewards.
