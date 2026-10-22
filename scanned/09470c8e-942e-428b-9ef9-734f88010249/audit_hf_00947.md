# [M] Missing whenNotPaused modifier for exitAll()

## Summary
Severity: Medium
Contest weight: 0.6530
Dataset id: 2997
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
withdraw() has the whenNotPaused modifier:
```solidity
function withdraw(uint256 amount, uint256 depositId) public whenNotPaused nonReentrant updateReward {
```
Therefore, when the contract is paused, users should not be able to withdraw their deposited tokens. However, the exitAll() function, which users can call to withdraw tokens from all their deposited positions, does not have the whenNotPaused modifier:
```solidity
function exitAll() external nonReentrant updateReward {
```
This is inconsistent with withdraw() since it wrongly allows users to withdraw even when the contract is paused.

## Recommendation
Add the missing whenNotPaused modifier to exitAll():
```solidity
function exitAll() external whenNotPaused nonReentrant updateReward {
```
