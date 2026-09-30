# [M] Incorrect calculation in maxBuyWithoutPenalty

## Summary
Severity: Medium
Contest weight: 0.5417
Dataset id: 8350
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The maxBuyWithoutPenalty function calculates the amount of tokens that can be purchased without penalty. But the formula for calculating expectedBalance is incorrect. It should use SNIPE_PROTECTED_SUPPLY instead of TOTAL_SUPPLY.
```solidity
function maxBuyWithoutPenalty() external view returns (uint256) {
    uint256 elapsedSeconds = block.timestamp - GENESIS_TIME;
    uint256 expectedBalance = TOTAL_SUPPLY - (TOTAL_SUPPLY * elapsedSeconds) / SNIPE_PROTECTION_SECONDS;
```

## Recommendation
Use SNIPE_PROTECTED_SUPPLY instead of TOTAL_SUPPLY.
```solidity
function maxBuyWithoutPenalty() external view returns (uint256) {
    uint256 elapsedSeconds = block.timestamp - GENESIS_TIME;
    uint256 expectedBalance = TOTAL_SUPPLY - (SNIPE_PROTECTED_SUPPLY * elapsedSeconds) / SNIPE_PROTECTION_SECONDS;
```
