# [M] Inconsistency referrerRebate

## Summary
Severity: Medium
Contest weight: 0.5822
Dataset id: 1779
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When opening the order, feeAfterRebate is calculated not to contain referrerRebate and vaultAllocation is calculated using feeAfterRebate. However, when closing the order, feeAfterRebate is calculated to contain referrerRebate. This is inconsistent fee allocation.  
In the, feeAfterRebate does not contain referrerRebate and vaultAllocation is calculated using feeAfterRebate. And this is paid to vault for opening fee.  
File: avantis-contracts\src\TradingStorage.sol  
L622:  
```solidity
uint vaultAllocation = (feeAfterRebate * (100 - _callbacks.vaultFeeP())) / 100;
uint govFees = (feeAfterRebate * _callbacks.vaultFeeP()) / 100 >> 1;
if (_usdc) IERC20(usdc).safeTransfer(address(vaultManager), vaultAllocation - referrerRebate);
vaultManager.allocateRewards(vaultAllocation - referrerRebate, false);
govFeesUSDC += govFees;
devFeesUSDC += feeAfterRebate - vaultAllocation - govFees;
```
When closing trade market, feeAfterRebate contains referrerRebate. However, when closing trade market, feeAfterRebate does not contain referrerRebate.  
In the, feeAfterRebate contains referrerRebate and vaultAllocation is calculated using feeAfterRebate. And this is paid to vault for closing fee.  
File: avantis-contracts\src\TradingCallbacks.sol  
L533:  
```solidity
uint vaultAllocation = ((feeAfterRebate - referrerRebate) * (100 - vaultFeeP)) / 100;
uint govFees = (feeAfterRebate - referrerRebate - vaultAllocation) / 2;
storageT.incrementClosingFees(feeAfterRebate - referrerRebate - vaultAllocation - govFees, govFees);
```
Internal pre-conditions  
None  
External pre-conditions  
1. None  
Attack Path  
None  
Fee allocation between opening and closing order is inconsistent

## Recommendation
Make referrerRebate fee allocation between opening and closing order consistent.
