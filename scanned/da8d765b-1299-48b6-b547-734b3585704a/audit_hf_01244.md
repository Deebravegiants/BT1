# [C] Excessive Payout in unstake and claim Functions Causes Severe Fund Loss

## Summary
Severity: Critical
Contest weight: 0.8526
Dataset id: 5753
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The unstake and claim functions incorrectly calculate the amount to transfer, resulting in users receiving 12 times the amount they originally staked. This leads to a significant loss of funds for the protocol.
The flawed calculation is shown here:
```solidity
let amount_to_transfer = self.position.amount
+ (self.position.amount * (12 - self.position.claimed as u64) * 10025 / 10000);
```
This miscalculation causes users to receive an excessive reward, far exceeding the intended staking rewards.

## Recommendation
The correct implementation should ensure that only a small portion of the staked amount is transferred per claim. Corrected Claim Function Calculation:
```solidity
let amount_to_transfer = self.position.amount * 25 / 10000;
```
Corrected Unstake Function Calculation: To properly transfer the unclaimed amount after the staking duration has passed:
```solidity
let amount_to_transfer =
self.position.amount + ((12 - self.position.claimed as u64) * self.position.amount * 25 / 10000);
```
