# [H] Loss of delegation rewards after unstaking

## Summary
Severity: High
Contest weight: 0.5715
Dataset id: 15609
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function Delegator#unstakePartial is responsible for partially unstaking a delegator’s funds. It performs multiple operations through StakeManager, including signaling redelegation, undelegating, signaling unstaking, and finally unstaking the specified amount. However, within StakeManager#undelegate, the delegates[msg.sender] value is reset to the zero address, meaning the delegator is no longer assigned to any validator.

The Overseer contract does not implement any function to call Delegator#delegate, preventing automatic re-delegation after an unstake operation. As a result, once a delegator unstakes, they will not be delegating to any validator, leading to a permanent loss of delegation rewards.

## Recommendation
Modify Delegator#unstakePartial to call stakeManager.delegate(validator) after unstaking, ensuring the delegator is immediately reassigned to a validator and continues earning rewards. The corrected implementation should be:
```solidity
function unstakePartial(uint256 amount) public onlyRole(OVERSEER_ROLE) {
    stakeManager.signalRedelegate();
    stakeManager.undelegate();
    stakeManager.signalUnstake();
    stakeManager.unstake(amount);
    elx.transfer(overseer, amount);
    stakeManager.delegate(validator);
}
```
This change ensures that delegation remains intact after unstaking, preventing unnecessary reward losses.
