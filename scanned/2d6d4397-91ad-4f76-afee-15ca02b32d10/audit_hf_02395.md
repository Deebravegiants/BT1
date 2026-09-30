# [M] Possible Underﬂow in FeeRewardDivider::distribute()

## Summary
Severity: Medium
Contest weight: 0.4625
Dataset id: 12924
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Rollup protocol has the built-in logic of distributing rewards to intended recipient. While reviewing the logic to distribute protocol fee rewards, we notice a possible arithmetic underﬂow issue.

To elaborate, we show below the related distribute() routine in FeeRewardDivider. The reward distribution is performed based on their percentages with the sum expected to be full in PRECISION. We notice it also supports the rebate program, which basically oﬀers discounts back to the trader and eﬀectively reduces the overall sum to be (PRECISION-leftPercent)/PRECISION. In other words, after the trader rebate, we need to distribute the rewards with adjusted percentage by scaling down with (PRECISION-leftPercent)/PRECISION (lines 50-51).

```solidity
function distribute(address _account, address _vault, uint256 _amount, bytes32 _uuid)
    external
    override
    onlyHandler
{
    if (recipients.length == 0) return;
    if (_amount == 0) revert("FeeRewardDivider:!amount");
    uint256 leftPercent = PRECISION;

    if (_account != address(0)) {
        if (_referral() != address(0)) {
            ReferralInfo memory _rInfo = IReferralStorage(_referral()).getTraderReferralInfo(_account);
            if (_rInfo.rebate > 0) {
                leftPercent -= (_rInfo.rebate + _rInfo.subRebate);
                uint256 rebateFee = _amount * (_rInfo.rebate + _rInfo.subRebate) / PRECISION;
                IReferralStorage(_referral()).distribute(_rInfo.referrer, _account, _vault, rebateFee, _uuid);
            }
        }
    }
    for (uint256 i = 0; i < (recipients.length - 1); i++) {
        uint256 amount = _amount * recipients[i].percent / PRECISION;
        leftPercent -= recipients[i].percent;
        if (amount > 0) {
            IStableVault(_vault).payoutReward(recipients[i].account, amount);
        }
    }
    if (leftPercent > 0) {
        uint256 amount = _amount * leftPercent / PRECISION;
        if (amount > 0) {
            IStableVault(_vault).payoutReward(recipients[recipients.length - 1].account, amount);
        }
    }
}
```

## Recommendation
Properly revise the above routine to take into account the trader rebate. Note a similar underﬂow issue is also present in other routines, including _emitIncreasePosition() and _emitDecreasePosition() in the Trading contract.
