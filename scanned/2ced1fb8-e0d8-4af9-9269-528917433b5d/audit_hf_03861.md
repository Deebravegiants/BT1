# [M] possible precision loss in

## Summary
Severity: Medium
Contest weight: 0.5425
Dataset id: 20122
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
finishLiquidation() divides before multiplying when calculating realDebt.  
```solidity
uint256 realDebt = borrows.div(record.interestIndex == 0 ? 1e18 : record.interestIndex).mul(info.borrowIndex);
```
There will be precision loss when calculating the realDebt because solidity truncates values when dividing and dividing before multiplying causes precision loss.  
Values that suffered from precision loss will be updated here  
```solidity
info.totalBorrows = info.totalBorrows - realDebt;
```
Values that suffered from precision loss will be updated here  
```solidity
info.totalBorrows = info.totalBorrows - realDebt;
```

## Recommendation
don't divide before multiplying
