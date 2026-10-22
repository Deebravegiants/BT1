# [M] EMI calculation is flawed

## Summary
Severity: Medium
Contest weight: 0.5677
Dataset id: 1932
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Taking min when calculating EMI repayment amount is flawed
The amount due in case of EMI repayment is calculated as:
ontracts/libraries/V2Calculations.sol#L124-L138
```solidity
} else {
    // Default to PaymentType.EMI
    // Max payable amount in a cycle
    //the amount owed for the cycle should never exceed the current payment cycle amount so we use min here
    uint256 owedAmountForCycle = Math.min(
        ((_bid.terms.paymentCycleAmount * owedTime) / _paymentCycleDuration),
        _bid.terms.paymentCycleAmount + interest_
    );
    uint256 owedAmount = isLastPaymentCycle ? owedPrincipal_ + interest_ : owedAmountForCycle;
    duePrincipal_ = Math.min(owedAmount - interest_, owedPrincipal_);
}
```
This is incorrect and leads to lowered payments since _bid.terms.paymentCycleAmount+in terest_ will be taken instead of the ratio wise amount
Eg: Principal (P) = 100 Annual Rate (r) = 12% = 0.12 Number of Monthly Payments (n) = 12 monthly EMI = 8.84
But if the repayment occurs after 2 months, this formula calculates the amount due as 8.84 + 2 == 10.84 instead of 8.84 * 2
Internal pre-conditions
External pre-conditions
Attack Path
Incorrectly lowered payments in case of EMI repayments

## Recommendation
Dont take the min. Instead use
```solidity
((_bid.terms.paymentCycleAmount * owedTime) / _paymentCycleDuration)
```
Disclaimers project. Usage of all smart contract software is at the respective users’ sole risk and is the users’ responsibility.
