# [M] Potential Lock of User Stakes

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 12814
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Project Chosen protocol shares an incentivizer mechanism that is inspired from Synthetix. In this section, we focus on a routine, i.e., rewardPerToken(), which is responsible for calculating the reward rate for each staked token. And it is part of the updateReward() modifier that would be invoked up-front for almost every public function in IgoOrePool to update and use the latest reward rate. The reason is due to the known potential underflow pitfall when the endTime parameter is inappropriately configured. In particular, as the rewardPerToken() routine involves the multiplication of three uint256 integers and the first integer depends on the lastTimeRewardApplicable().sub(lastUpdateTime) (lines 114-115). While the endTime parameter is configured to be smaller than lastUpdateTime, it may result in an undesirable underflow, which effectively reverts the rewardPerToken() execution!
```solidity
function lastTimeRewardApplicable() public view returns (uint256) {
    return Math.min(block.timestamp, endTime);
}
function rewardPerToken() public view returns (uint256) {
    if (totalPower == 0) {
        return intervalReward;
    }
    return intervalReward.add(
        lastTimeRewardApplicable()
            .sub(lastUpdateTime)
            .mul(miningOutput)
            .mul(1e18)
            .div(totalPower)
    );
}
function updateStartTime(uint256 _time) public onlyOperator {
    startTime = _time;
}
function updateEndTime(uint256 _time) public onlyOperator {
    endTime = _time;
}
function updateMiningOutput(uint256 _yield) public onlyOperator {
    intervalReward = rewardPerToken();
    lastUpdateTime = lastTimeRewardApplicable();
    miningOutput = _yield;
}
```
The underflow may in essence lock all deposited funds! Note that an authentication check on the caller of onlyOperator() greatly alleviates such concern. Currently, only the operator address is able to call updateEndTime() and this address can be set when the contract is deployed. Apparently, if the operator is a normal address, it may put users funds at risk. To mitigate this issue, it is necessary to have the ownership under the governance control and ensure the endTime parameter will not be configured to underflow and lock users funds.

## Recommendation
Mitigate the potential underflow risk in the IgoOrePool pool.
