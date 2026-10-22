# [M] Updating `operatorRewardPercentage` incorrectly redistributes already accrued rewards

## Summary
Severity: Medium
Contest weight: 0.4445
Dataset id: 22227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `operatorRewardPercentage` in L1Strategy determines how rewards are split between operators and other recipients. When this percentage is changed, previously generated but undistributed rewards are calculated using the new percentage rather than the percentage that was in effect when they were generated.

Key code in `SequencerVault.sol` where rewards are calculated:
```solidity
// SequencerVault.sol
function updateDeposits(
    uint256 _minRewards,
    uint32 _l2Gas
) external payable onlyVaultController returns (uint256, uint256, uint256) {
    // Calculate total deposits and changes
    uint256 principal = getPrincipalDeposits();
    uint256 rewards = getRewards();
    uint256 totalDeposits = principal + rewards;
    int256 depositChange = int256(totalDeposits) - int256(uint256(trackedTotalDeposits));

    uint256 opRewards;
    if (depositChange > 0) {
        // Uses current operatorRewardPercentage for all accrued rewards
        opRewards = (uint256(depositChange) * vaultController.operatorRewardPercentage()) / 10000;
        trackedTotalDeposits = SafeCastUpgradeable.toUint128(totalDeposits);
    }
    //...
}
```
Consider the following scenario:

- operatorRewardPercentage = 10%
- 100 tokens of rewards accrue (10 for operators, 90 for others)
- operatorRewardPercentage changed to 25%
- On next update, same 100 tokens are split: 25 for operators, 75 for others
- Recipients lose 15 tokens they had effectively earned

Changing percentage up: Other recipients lose already earned rewards
Changing percentage down: Operators lose already earned rewards

## Recommendation
Consider distributing the already earned rewards (if any) using the current `operatorRewardPercentage` before updating it to a new value. This would involve updating the deposits on the Strategy (which in turn would update the deposits on the SequencerVaults), and, send an update the L2 to mint the corresponding shares for the earned rewards.
