# [M] Sum of fee percentages might not be equal to the admin provided total value

## Summary
Severity: Medium
Contest weight: 0.1278
Dataset id: 3368
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The input validation for the newFeePercents in the _changeFee method looks like this:
(newFeePercents.lp + newFeePercents.front + newFeePercents.dao) >
FixedMath.ONE ||
newFeePercents.total > FixedMath.ONE
) revert IncorrectValue();
While both the sum of the fee percentages and the total value are validated that they are not more than 100%, it is possible that the sum of the three different fee percentages is not equal to the total value. Now if they actually amount to different values this will mess up the accounting of the contract, as when a user puts a bet then the fee.total is removed from his bet amount, but then different values would be sent to the fee recipients. This will result in either stuck funds or direct value loss for the protocol & its users.

## Recommendation
Change the code in the following way:
- (newFeePercents.lp + newFeePercents.front + newFeePercents.dao) >
- FixedMath.ONE ||
+ (newFeePercents.lp + newFeePercents.front + newFeePercents.dao) != newFeePercents.total
newFeePercents.total > FixedMath.ONE
) revert IncorrectValue();
