# [M] Lower ezETH Mint Rate Due To Rounding

## Summary
Severity: Medium
Contest weight: 0.5604
Dataset id: 14452
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ezETH mint amount calculation performs multiple divisions, resulting in rounding errors that cause mintAmount to be less than intended.
RenzoOracle::calculateMintAmount() calculates the ezETH mintAmount as follows:
```solidity
// Calculate the percentage of value after the deposit
uint256 inflationPercentaage = (SCALE_FACTOR * _newValueAdded) / (_currentValueInProtocol + _newValueAdded);
// Calculate the new supply
uint256 newEzETHSupply = (_existingEzETHSupply * SCALE_FACTOR) / (SCALE_FACTOR - inflationPercentaage);
// Subtract the old supply from the new supply to get the amount to mint
uint256 mintAmount = newEzETHSupply - _existingEzETHSupply;
```
inflationPercentaage is calculated through a mulDiv, and then used again in another mulDiv to calculate newEzETHSupply. This results in more rounding errors that reduce the ezETH mintAmount.
Furthermore, due to less ezETH being minted, xezETH tokens on L2s end up being undercollateralised by ezETH tokens in the xezETHLockbox in L1.

## Recommendation
Instead of performing two mulDivs and then a subtraction to calculate mintAmount, use the following expression to calculate mintAmount with one mulDiv:
```solidity
uint256 mintAmount = (_existingEzETHSupply * _newValueAdded) / _currentValueInProtocol;
```
