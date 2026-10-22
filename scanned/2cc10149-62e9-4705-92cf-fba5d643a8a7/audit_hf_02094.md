# [H] Revisited Precision in MaGaugeV2Upgradeable::rewardPerToken()

## Summary
Severity: High
Contest weight: 0.5891
Dataset id: 11818
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the MaGaugeV2Upgradeable contract implements an incentive mechanism that rewards the staking of the supported LP token with the CHR token. In particular, one entry routine, i.e., rewardPerToken(), is designed to calculate the accumulated reward per token. While examining its logic, we observe its precision calculation needs to be improved.

To elaborate, we show below the related code snippet of the contract. Inside the rewardPerToken() routine, the formula of rewardPerTokenStored + (((lastTimeRewardApplicable()- lastUpdateTime)* rewardRate * 1e18)/ _totalWeight) is used to calculate the accumulated reward per token. If we only focus on its precision, it can be simplified as 1e18 * 1e18 / 1e18 * 1e18 = 1 (assuming the decimals of the rewardToken is 18). The precision of the accumulated reward per token should be 1e18 by design and thus the formula is incorrect.
```solidity
function rewardPerToken() public view returns (uint) {
    if (_totalWeight == 0) {
        return rewardPerTokenStored;
    } else {
        return rewardPerTokenStored +
            (((lastTimeRewardApplicable() - lastUpdateTime) *
            rewardRate *
            1e18) / _totalWeight);
    }
}
```

## Recommendation
Revisit the precision calculation in above-mentioned routine.
