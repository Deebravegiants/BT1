# [M] LeverEPTActions#buyCollateralAndIncreaseLeve

## Summary
Severity: Medium
Contest weight: 0.1613
Dataset id: 17627
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because of the precision loss in the conversion of borrowed amount (addDebt) to deltaNormalDebt with wdiv(addDebt, rate), the newly generated internal credit for FIAT (deltaDebt) will most certainly always be 1 Wei less than addDebt.  
As a result, the buyCollateralAndIncreaseLever() will fail due to insufficient credit in codex.transferCredit().  
When buyCollateralAndIncreaseLever() is called, it will take a flashloan from flash which will callback and call the internal function addCollateralAndDebt() with the amount of addCollateral and borrowed (as addDebt).  
codex.modifyCollateralAndDebt() will then be called with deltaNormalDebt = wdiv(addDebt, rate); In codex.modifyCollateralAndDebt(), the deltaNormalDebt will be convert back as int256 deltaDebt = wmul(v.rate, deltaNormalDebt);.  
The back and forth conversion will most certainly incur a precision loss, resulting in the deltaDebt to be 1 Wei smaller than addDebt.  
Thus, the transaction will revert in exitMoneta(creditor, addDebt); as the credit will be insufficient (by 1 Wei).  
LeverEPTActions#buyCollateralAndIncreaseLever() will most certainly fail.

## Recommendation
Consider using wdivUp() for deltaNormalDebt = wdiv(addDebt, rate).  
Fix: https://github.com/fiatdao/actions/pull/12
