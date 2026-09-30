# [M] BnGMX Reduction Minimization with JIT StakedGMX Inflation

## Summary
Severity: Medium
Contest weight: 0.4595
Dataset id: 11719
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To incentivize the long-time stakers without inflation, the BeamEx protocol has a so-called multiplier points. Speciﬁcally, when a user stakes the governance token, the user will receive multiplier points every second at a ﬁxed rate of 100% APR. When GMX or Escrowed GMX tokens are unstaked, the proportional amount of multiplier points are burnt. While reviewing the current unstaking logic, we notice the current implementation can be improved. To elaborate, we show below the related _unstakeGmx() routine. As the name indicates, this routine is used to unstake GMX with the necessary support of burning the proportional multiplier points. However, it comes to our attention that the computed amount of multiplier points to burn may be manipulated to retain the majority of multiplier points.

```solidity
function _unstakeGmx(address _account, address _token, uint256 _amount) private {
    require(_amount > 0, "RewardRouter: invalid _amount");
    uint256 balance = IRewardTracker(stakedGmxTracker).stakedAmounts(_account);
    IRewardTracker(feeGmxTracker).unstakeForAccount(_account, bonusGmxTracker, _amount, _account);
    IRewardTracker(bonusGmxTracker).unstakeForAccount(_account, stakedGmxTracker, _amount, _account);
    IRewardTracker(stakedGmxTracker).unstakeForAccount(_account, _token, _amount, _account);
    uint256 bnGmxAmount = IRewardTracker(bonusGmxTracker).claimForAccount(_account, _account);
    if (bnGmxAmount > 0) {
        IRewardTracker(feeGmxTracker).stakeForAccount(_account, _account, bnGmx, bnGmxAmount);
    }
    uint256 stakedBnGmx = IRewardTracker(feeGmxTracker).depositBalances(_account, bnGmx);
    if (stakedBnGmx > 0) {
        uint256 reductionAmount = stakedBnGmx.mul(_amount).div(balance);
        IRewardTracker(feeGmxTracker).unstakeForAccount(_account, bnGmx, reductionAmount, _account);
        IMintable(bnGmx).burn(_account, reductionAmount);
    }
    emit UnstakeGmx(_account, _amount);
}
```

Here is an example list of steps that can avoid the burn of most multiplier points. For simplicity, let's assume the user Malice has staked GMX and he wishes to unstake GMX while minimizing the amount of bnGMX burnt.
1. Malice initially calls IRewardTracker(stakedGmxTracker).stake(GMX, JIT_AMOUNT) to increase the staked GMX balance, i.e., with the addition of JIT_AMOUNT.
2. Malice performs the unstaking call, i.e., RewardRouter.unstakeGmx(). Note the calculation of reduced bnGMX amount is shown as follows: bnGMX = bnGMX balance * GMX amount unstaked / GMX balance. Since the staked GMX balance is increased, a smaller bnGMX amount to burn is derived.
3. Malice calls IRewardTracker(stakedGmxTracker).unstake(GMX, JIT_AMOUNT) to unstake the JITed GMX balance JIT_AMOUNT.

## Recommendation
Revise the above unstaking logic to reliably compute the bnGMX amount to burn.
