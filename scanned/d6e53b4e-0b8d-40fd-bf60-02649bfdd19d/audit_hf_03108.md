# [H] Staggered vesting’s getClaimableAmount computes wrong awardAmount

## Summary
Severity: High
Contest weight: 0.1858
Dataset id: 17528
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getClaimableAmount function computes the awardAmount from the staggered vesting plan as _staggeredPlan.cliffAmount + (_staggeredPlan.cadence * _staggeredPlan.tokenAmountPerPeriod). This is incorrect because the cadence reflects the length (in seconds) of a period, whereas the token amount per period should be multiplied by the total number of periods. The impact is that this value will be highly overestimated. The current StaggeredVestingModule does indeed ignore this value for its computations and is not needed. awardAmount in the module can be fatal and lead to vesting funds being stolen.

## Recommendation
It is recommended to change the design of the deposit and withdrawal process so that funds can be processed without a queue. Users should be able to process their deposits or withdrawals regardless of a specific order. uint256 awardAmount = _staggeredPlan.cliffAmount + (_staggeredPlan.totalVestingPeriods * _staggeredPlan.tokenAmountPerPeriod); Confirmed
