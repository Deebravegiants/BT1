# [M] Base interest can change while there is uncol-

## Summary
Severity: Medium
Contest weight: 0.3912
Dataset id: 17642
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
baseInterest can be modified at any time, while there may be uncollected interest.  
The interestPerSecond setter has a check to ensure that there is all interest has been collected prior to changing its value.  
```solidity
if (block.timestamp != vaults[vault].lastCollected) revert Publican__setParam_notCollected();
```  
"Global, per-second stability fee contribution", so it seems that it should only be modified when all interest has been collected too.  
Base interest rate update is retroactively applied to uncollected interest, which may be undesirable.

## Recommendation
Include the referenced conditional check in the setter for baseInterest.  
Interest collection happens every 3 days and every time a user interacts with the protocol. There could be a loss, but it would be insignificant. Additionally the current behavior solves the problem of the last depositor being unable to pay off accrued interest because there's not enough FIAT in circulation. In a situation like this the DAO may set the rate to 0.
