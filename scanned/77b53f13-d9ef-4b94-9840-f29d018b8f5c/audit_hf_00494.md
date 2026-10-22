# [H] Updating earning power for de-

## Summary
Severity: High
Contest weight: 0.7692
Dataset id: 1945
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description
When the earning power (total or per deposit) changes, rewards are checkpointed to avoid manipulation. Unfortunately for the functions alterDelegatee and alterClaimer the rewards are not updated and this can lead draining of rewards for all participants as described in the scenario below
Scenario
Pre-conditions
• BinaryEligibilityOracleEarningPowerCalculator is used as earning power calculator
• There exists one delegatee D_valid which has a 100 score, and a delegatee D_invalid with a zero score.
• Alice has a position of balance 500 delegated to D_valid
• Total earning power in GovernanceStaker is 1000
Steps
Some time passes and Alice is eligible for rewards, instead of claiming them directly, Alice does the following:
• Alice delegates her position to D_invalid, total earning power becomes 500
• Alice checkpoints global rewards (for example Alice can create a small new position)
• Alice delegates her position to D_valid, her earning power is now 500 but rewardsPerTokenAccumulated has been computed with totalEarningPower being 500. This means Alice claims the rewards which were meant for all participants.
terClaimer but it is safe in doing so, because these functions do not modify individual earning powers.
All of the rewards available at a given time can be drained by a malicious depositor

## Recommendation
Please consider adding checkpointing of rewards to _alterDelegatee and _alterClaimer:
GovernanceStaker.sol#L619-L624:
```solidity
function _alterDelegatee(
    Deposit storage deposit,
    DepositIdentifier _depositId,
    address _newDelegatee
) internal virtual {
    _revertIfAddressZero(_newDelegatee);
    _checkpointGlobalReward();
    _checkpointReward(deposit);
```
GovernanceStaker.sol#L645-L650:
```solidity
function _alterClaimer(
    Deposit storage deposit,
    DepositIdentifier _depositId,
    address _newClaimer
) internal virtual {
    _revertIfAddressZero(_newClaimer);
    _checkpointGlobalReward();
    _checkpointReward(deposit);
```
