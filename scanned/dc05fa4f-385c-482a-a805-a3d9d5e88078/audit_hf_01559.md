# [M] Bypass minimumDeployVestTime due to vestingEnd overflow

## Summary
Severity: Medium
Contest weight: 0.5931
Dataset id: 8345
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The g8keepFactory contract implements a minimum vesting period for token deployers through the minimumDeployVestTime parameter. However, an error in the g8keepVester contract allows this check to be bypassed due to potential timestamp overflow.
In the deployToken function of g8keepFactory, there's a check to ensure the vesting time meets the minimum requirement:
```solidity
function deployToken(
    uint256 _initialLiquidity,
    string memory _name,
    string memory _symbol,
    uint256 _totalSupply,
    address _treasuryWallet,
    uint8 _buyFee,
    uint8 _sellFee,
    address _pairedToken,
    uint256 _deployReserve,
    uint256 _deployVestTime,
    uint256 _snipeProtectionSeconds,
    bytes32 _tokenSalt
) external payable returns (address _tokenAddress) {
    if (_buyFee > maxBuyFee || _sellFee > maxSellFee || _deployVestTime < minimumDeployVestTime) revert InvalidDeploymentParameters();
```
However, in the g8keepVester contract, the deploymentVest function stores the vesting end time as a uint40, which can lead to an overflow. This overflow can result in a much shorter vesting period than intended, potentially allowing immediate token claims.
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
    deploymentVesting.vestingEnd = uint40(block.timestamp + _vestTime); // @audit vestingEnd can overflow
```
This vulnerability allows malicious deployers to bypass the minimum vesting period set by g8keep. They could set a very large _deployVestTime that causes an overflow, resulting in a near-immediate vesting end time. This undermines the intended token distribution model and could lead to an unexpected token dump.

## Recommendation
Check if block.timestamp + _vestTime is more than type(uint40).max and revert if it is.
