# [H] Revert in closeSuccessfulDrop can cause tokens to be permanently stuck

## Summary
Severity: High
Contest weight: 0.8717
Dataset id: 3764
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The closeSuccessfulDrop function in the ColonyDropManager contract can fail due to an underflow in the payout calculation logic. This happens when the combined values of totalPaidOut and commissionFee exceed totalRaised. The failure results in a revert, making it impossible to close the drop and release funds. Without an emergency recovery mechanism, any tokens remaining in the contract will be permanently locked. Root Cause The vulnerability lies in the _handleCloseSuccesfulDropPayouts function. Specifically, the issue arises during the calculation of amountToSendToCreator: Vulnerable Code
```solidity
uint256 amountToSendToCreator = (totalRaised - _amountRaised.totalPaidOut)
- commissionFee;
```
If the sum of _amountRaised.totalPaidOut and commissionFee is greater than totalRaised, the subtraction causes an underflow. For instance: ). Assume: totalRaised = 600 totalPaidOut = 500 commissionFee = 120 (20% of totalRaised) *. The calculation for amountToSendToCreator becomes: amountToSendToCreator = (600 - 500) - 120; // -20% +. Since amountToSendToCreator is unsigned, this underflow triggers a revert.

## Recommendation
Ensure that totalPaidOut and commissionFee do not exceed totalRaised before performing the calculation. For example:
```solidity
require(totalPaidOut + commissionFee <= totalRaised, "Invalid payout parameters");
```
Another way can be to modify the payout logic to prevent underflows:
```solidity
uint256 availableFunds = totalRaised > totalPaidOut ? totalRaised - totalPaidOut : 0;
uint256 amountToSendToCreator = availableFunds > commissionFee ? availableFunds - commissionFee : 0;
```
This ensures amountToSendToCreator never becomes negative.
