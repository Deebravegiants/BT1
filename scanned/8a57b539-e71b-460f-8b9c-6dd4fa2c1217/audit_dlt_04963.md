# [H] Increasing the lock malfunction

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/93
Type: sherlock-finding

## Details
HonorLt

high

# Increasing the lock malfunction

## Summary
When increasing the locked amount, the function mistakenly checks against the old deposit of the caller but updates the receiver.

## Vulnerability Detail
```increaseLock``` queries the deposit of ```_msgSender```:
```solidity
  Deposit memory userDeposit = depositsOf[_msgSender()][_depositId];
```
and does all the calculations of duration, and minting accordingly, but finally writes the data to the deposits of the receiver:
```solidity
  depositsOf[_receiver][_depositId].amount += _increaseAmount;
  depositsOf[_receiver][_depositId].shareAmount += mintAmount;
```

## Impact
This mess up data and validations, for instance, the expiration check becomes pointless making it possible to increase the amount of an already expired deposit, and the assets are lost this way.

## Code Snippet

```solidity
        Deposit memory userDeposit = depositsOf[_msgSender()][_depositId];
        ...
        uint256 remainingDuration = uint256(userDeposit.end - block.timestamp);
        uint256 mintAmount = _increaseAmount * getMultiplier(remainingDuration) / 1e18;

        depositsOf[_receiver][_depositId].amount += _increaseAmount;
        depositsOf[_receiver][_depositId].shareAmount += mintAmount;
````

## Tool used

Manual Review
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/93_
