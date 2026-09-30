# [M] rewardData.releaseRate is incorrectly calcu

## Summary
Severity: Medium
Contest weight: 0.4343
Dataset id: 22776
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Setting new parameters in RewardsController::config() will lead to lost rewards if block.timestamp > start and the rewardData.start was set in the future initially.

When RewardsController::config() is called to update the data of a reward, as it was already set initially, it will go into the else branch. In here, it updates the rewardRate according to the previously distributed rewards, the total distribution and the distribution periods. More precisely, the calculation is:
```solidity
if (block.timestamp > start) {
    released = rewardData.lastConfigReleased + rewardData.releaseRate * (block.timestamp - rewardData.lastConfig);
    elapsed = block.timestamp - start;
    if (configs[i].totalDistribution <= released || configs[i].distributionPeriod <= elapsed) {
        revert InvalidConfig();
    }
    rewardData.lastConfigReleased = released;
}
rewardData.releaseRate = (configs[i].totalDistribution - released) / (configs[i].distributionPeriod - elapsed);
```
It calculates the release pro-rata to block.timestamp - rewardData.lastConfig, considering the time that the rewards have been emitted, but this is incorrect when rewardData.start was set in the future when creating the initial config. This will lead to the overestimation of released rewards, which will lower the rewardData.releaseRate, as it is pro-rata to configs[i].totalDistribution - released. Thus, less rewards will be distributed than expected.

Lost of rewards for users that will receive less than supposed.

## Recommendation
The release rewards are rewardData.releaseRate * (block.timestamp - rewardData.start);
