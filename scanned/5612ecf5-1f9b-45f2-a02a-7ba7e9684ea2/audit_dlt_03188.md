# [M] Mitigation Confirmed for M-04

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/16
Type: code-finding

## Details
Note: Issue has not actually been resolved but for some reason I can't get my issues to submit without "Mitigation confirmed (no new vulnerabilities detected)" checked so I am doing this as a work around

## Severity

Medium

## Lines of code

https://github.com/asymmetryfinance/smart-contracts/pull/228/files#diff-6abc8f2e4ad1647a12784e9fbf18e9c5f86c05668e3e89e2a51ab569992b214fR111-R116

## Impact

## Proof of Concept

The root cause of M-04 has still not been addressed since the contract still doesn't allow the user to specify a deadline. This makes the vulnerability presented in the original submission to still be valid.

## Tools Used

Manual Review

## Recommended Mitigation Steps

Implement a deadline check on both withdrawals and deposits in the safETH.sol contract:

    -   function stake() external payable returns (uint256 mintedAmount) {
    +   function stake(uint256 deadline) external payable returns (uint256 mintedAmount) {
    +       require(block.timestamp <= deadline);
            require(pauseStaking == false, "staking is paused");
            require(msg.value >= minAmount, "amount too low");
