# [H] Preventing token claims until vesting period ends

## Summary
Severity: High
Contest weight: 0.8949
Dataset id: 8357
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The g8keepVester contract, responsible for managing token vesting schedules, contains an error in its implementation that prevents users from claiming any tokens until the entire vesting period has elapsed.
The issue stems from the deploymentVest function not initializing the lastClaim timestamp when creating a new vesting schedule:
```solidity
function deploymentVest(address _deployer, uint256 _tokensToDeployer, uint256 _vestTime)
    external
    returns (uint256 vestingId)
{
    DeploymentVesting storage deploymentVesting = deploymentVestings[vestingId];
    deploymentVesting.recipient = _deployer;
    deploymentVesting.token = msg.sender;
    deploymentVesting.amount = _tokensToDeployer;
    deploymentVesting.vestingStart = uint40(block.timestamp);
    deploymentVesting.vestingEnd = uint40(block.timestamp + _vestTime); // @audit lastClaim is not set
```
This omission causes the _vested function to calculate an inflated vestedAmount:
```solidity
function _vested(uint256 _id) internal view returns (DeploymentVesting storage vesting, uint256 vestedAmount) {
    vesting = deploymentVestings[_id];
    uint256 vestingStart = vesting.vestingStart;
    if (block.timestamp < vestingStart) return (vesting, 0);
    uint256 vestingEnd = vesting.vestingEnd;
    uint256 vestingAmount = vesting.amount;
    uint256 vestingClaimed = vesting.claimed;
    if (block.timestamp >= vestingEnd) return (vesting, (vestingAmount - vestingClaimed));
    uint256 timeSinceLastClaim = block.timestamp - vesting.lastClaim; // @audit inflated since lastClaim is 0
    uint256 vestingPeriod = vestingEnd - vestingStart;
    vestedAmount = (vestingAmount * timeSinceLastClaim) / vestingPeriod; // @audit vestedAmount
```
Consequently, when a user attempts to claim tokens via the claim function, the transaction will revert due to insufficient balance, as the calculated vestedAmount exceeds the total vesting amount.

## Recommendation
Initialize the lastClaim timestamp in the deploymentVest function:
```solidity
function deploymentVest(address _deployer, uint256 _tokensToDeployer, uint256 _vestTime)
    external
    returns (uint256 vestingId)
{
    DeploymentVesting storage deploymentVesting = deploymentVestings[vestingId];
    deploymentVesting.recipient = _deployer;
    deploymentVesting.token = msg.sender;
    deploymentVesting.amount = _tokensToDeployer;
    deploymentVesting.vestingStart = uint40(block.timestamp);
    deploymentVesting.vestingEnd = uint40(block.timestamp + _vestTime);
    deploymentVesting.lastClaim = uint40(block.timestamp);
```
