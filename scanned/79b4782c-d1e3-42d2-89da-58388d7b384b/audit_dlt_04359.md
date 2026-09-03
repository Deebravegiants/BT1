# [M] User's fund is locked if the admin pause the contract

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/128
Type: sherlock-finding

## Details
ctf_sec

medium

# User's fund is locked if the admin pause the contract

## Summary

Admin paused feature block user from withdrawal their fund.

## Vulnerability Detail

User can stake or unstake via UserManager.sol

```solidity
    function stake(uint96 amount) public whenNotPaused nonReentrant {
```

and 

```solidity
    function unstake(uint96 amount) external whenNotPaused nonReentrant {
```

however, when if the admin pauses the contract via controller.

```solidity
function pause() external onlyGuardian whenNotPaused {
    _paused = true;
    emit LogPaused(msg.sender);
}
```

 the fund is locked and the user is not able to able to get their fund back until the admin unpause the contract.

## Impact

If the admin pause the contract, the pause can block user from withdrawing their unstake and withdraw.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/128_
