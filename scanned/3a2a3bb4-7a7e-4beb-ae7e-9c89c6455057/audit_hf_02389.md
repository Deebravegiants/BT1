# [M] Incorrect Reward-Sending Logic in RadiantStaking

## Summary
Severity: Medium
Contest weight: 0.4582
Dataset id: 12878
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Radpie protocol has a key RadiantStaking contract that enables users zap into DLP positions to get boosted yield and vote. In the process of examining the current logic of sending out rewards, we notice the implementation has an issue that needs to be fixed. To elaborate, we show below the implementation of the related _sendRewards() routine. This routine has a straightforward logic in sending out rewards to intended recipients. Note that the leftover funds, if any, is sent to the protocol owner. However, it comes to our attention that the leftover funds are sent with the first argument _asset, instead of _rewardToken. Also, the leftover amount is currently computed as rewardLeft - _amount (line 706), instead of rewardLeft.
```solidity
function _sendRewards(address _asset, address _rewardToken, uint256 _amount) internal {
    if (_amount == 0) return;
    Fees[] storage feeInfos;
    if (_rewardToken == address(rdnt)) feeInfos = radiantFeeInfos;
    else feeInfos = rTokenFeeInfos;
    for (uint256 i = 0; i < feeInfos.length; i++) {
        Fees storage feeInfo = feeInfos[i];
        if (!feeInfo.isActive) continue;
        address rewardToken = _rewardToken;
        uint256 feeAmount = (_amount * feeInfo.value) / DENOMINATOR;
        uint256 feeTosend = feeAmount;
        if (!feeInfo.isAddress) {
            IERC20(rewardToken).safeApprove(feeInfo.to, feeTosend);
            IBaseRewardPool(feeInfo.to).queueNewRewards(feeTosend, rewardToken);
        } else {
            IERC20(rewardToken).safeTransfer(feeInfo.to, feeTosend);
        }
        emit RewardPaidTo(_asset, feeInfo.to, rewardToken, feeTosend);
    }
    // if there is somehow reward left, sent it to owner
    uint256 rewardLeft = IERC20(_rewardToken).balanceOf(address(this));
    if (rewardLeft > _amount) {
        IERC20(_asset).safeTransfer(owner(), rewardLeft - _amount);
        emit RewardFeeDustTo(_rewardToken, owner(), rewardLeft - _amount);
    }
}
```

## Recommendation
Revise the above routine to properly send out rewards.
