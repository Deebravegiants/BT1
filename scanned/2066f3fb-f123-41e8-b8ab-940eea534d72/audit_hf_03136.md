# [H] increaseLock() should read userDeposit[_rece

## Summary
Severity: High
Contest weight: 0.5601
Dataset id: 17621
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TimeLockPool.sol L203 should read depositsOf[_receiver][_depositId] as userDeposit.  
TimeLockPool.sol L230 in increaseLock() is loading depositsOf[_msgSender()][_depositId] as userDeposit, which will later be used to check if the deposit has expired (L206-208) and calculating the remainingDuration (L213).  
This remainingDuration will be used to calculate the multiplier for the mintAmount at L215.  
As a result, the _receiver can receive a much larger shares.  
For example, if the receiver only has 10 mins left in depositsOf[_receiver][_depositId], but depositsOf[_msgSender()][_depositId] have 4 years left. The mintAmount will be 5x than expected.  
Or fewer shares than expected when the caller's deposit's remainingDuration is shorter than the receiver's.

## Recommendation
Change L203 to:  
```solidity
Deposit memory userDeposit = depositsOf[_receiver][_depositId];
```
