# [C] claimRecurPool does not verify the provided incentiveToken is equal to rewardToken

## Summary
Severity: Critical
Contest weight: 0.2987
Dataset id: 4137
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It can be observed that when claimRecurPool is called, it doesn't verify if the incentiveToken provided is equal to the claimed RecurPoolKey's rewardToken.
```solidity
function claimRecurPool(
    RecurClaimParams[] calldata params,
    address recipient
) external nonReentrant {
    address msgSender = LibMulticaller.senderOrSigner();
    for (uint256 i; i < params.length; i++) {
        address incentiveToken = params[i].incentiveToken;
        uint256 totalClaimableAmount;
        for (uint256 j; j < params[i].keys.length; j++) {
            RecurPoolKey calldata key = params[i].keys[j];
            RecurPoolId id = key.toId();
            // key should be valid
            if (!isValidRecurPoolKey(key)) continue;
            // -------------------------------------------------------------------
            /// Storage loads
            // -------------------------------------------------------------------
            // load state
            RecurPoolState storage state = recurPoolStates[id];
            uint64 lastUpdateTime = state.lastUpdateTime;
            uint64 periodFinish = state.periodFinish;
            uint64 lastTimeRewardApplicable =
                block.timestamp < periodFinish ? uint64(block.timestamp) : periodFinish;
            uint256 rewardPerTokenUpdated = _rewardPerToken(
                state.rewardPerTokenStored,
                state.totalSupply,
                lastTimeRewardApplicable,
                lastUpdateTime,
                state.rewardRate
            );
            // -------------------------------------------------------------------
            /// State updates
            // -------------------------------------------------------------------
            // accrue rewards
            uint256 reward = _earned(
                state.userRewardPerTokenPaid[msgSender],
                state.balanceOf[msgSender],
                rewardPerTokenUpdated,
                state.rewards[msgSender]
            );
            state.rewardPerTokenStored = rewardPerTokenUpdated;
            state.lastUpdateTime = lastTimeRewardApplicable;
            state.userRewardPerTokenPaid[msgSender] = rewardPerTokenUpdated;
            if (reward != 0) {
                // delete accrued rewards
                delete state.rewards[msgSender];
                // accumulate claimable amount
                totalClaimableAmount += reward;
            }
        }
        // transfer incentive tokens to user
        if (totalClaimableAmount != 0) {
            // @audit - incentiveToken is not checked!
            incentiveToken.safeTransfer(recipient, totalClaimableAmount);
            // emit event
            emit ClaimReward(msgSender, incentiveToken, recipient, totalClaimableAmount);
        }
    }
}
```
An attacker can exploit this by creating a fake Recur Pool and providing an arbitrary/worthless rewardToken to increase its rewardRate. Then, when claimRecurPool is called, the attacker can set incentiveToken to another token that they want to steal from MasterBunni.

## Recommendation
Validate that the provided incentiveToken is equal to the rewardToken of each RecurPoolKey.
