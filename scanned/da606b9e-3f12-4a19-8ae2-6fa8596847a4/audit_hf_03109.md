# [H] Staggered vesting’s _awardAmount is never verified when claiming tokens

## Summary
Severity: High
Contest weight: 0.1466
Dataset id: 17536
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _awardAmount parameter can be chosen by the claimTokens caller. This value is never verified although it should equal _staggeredPlan.cliffAmount + (_staggeredPlan.totalVestingPeriods * _staggeredPlan.tokenAmountPerPeriod). This unchecked value is then forwarded to the IModule(module).claimable call. The current StaggeredVestingModule does indeed ignore this value for its computations and is not needed. awardAmount in the module can be fatal and lead to vesting funds being stolen.

## Recommendation
The claimTokens function does not need the _awardAmount as a parameter, it can be computed from the _staggeredPlan parameter, similar to getClaimableAmount. Confirmed
