# [M] Funds can be drained to 0 if bad settings are passed through proposal

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/49
Type: sherlock-finding

## Details
koxuan

medium

# Funds can be drained to 0 if bad settings are passed through proposal

## Summary
if `refundCooldown` is set to 0, it will enable users to delegate and `stake and unstake` infinitely, allowing attackers to drain all DAO funds by gas refunds

## Vulnerability Detail
refundCooldown is used by `delegate` and `stake` in Staking.sol to determine whether a user is eligible to claim gas refund based on the time of his previous attempts to delegate or stake. With `refundCooldown` set to 0, users will always be eligible for gas refund regardless of his previous attempts, enabling them to infinitely `delegate` and `stake and unstake then stake`, draining DAO funds as a result of all the gas refunds.

`  if (stakingRefund && lastStakingRefund[msg.sender] + refundCooldown <= block.timestamp) ` will always be true with stakingRefund being True and refundCooldown being 0.
```solidity
  function stake(uint[] calldata _tokenIds, uint _unlockTime) public {
    // Refunds gas if stakingRefund is true and hasn't been used by this user in the past 24 hours
    if (stakingRefund && lastStakingRefund[msg.sender] + refundCooldown <= block.timestamp) {
      uint256 startGas = gasleft();
      _stake(_tokenIds, _unlockTime);
      lastStakingRefund[msg.sender] = block.timestamp;
      _refundGas(startGas);
    } else {
      _stake(_tokenIds, _unlockTime);
    }
  }
```
same for `  if (delegatingRefund && lastDelegatingRefund[msg.sender] + refundCooldown <= block.timestamp)  `
```solidity
  function delegate(address _delegatee) public {
    if (_delegatee == address(0)) _delegatee = msg.sender;
    
    // Refunds gas if delegatingRefund is true and hasn't been used by this user in the past 24 hours
    if (delegatingRefund && lastDelegatingRefund[msg.sender] + refundCooldown <= block.timestamp) {
      uint256 startGas = gasleft();
      _delegate(msg.sender, _delegatee);
      lastDelegatingRefund[msg.sender] = block.timestamp;
      _refundGas(startGas);
    } else {
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/49_
