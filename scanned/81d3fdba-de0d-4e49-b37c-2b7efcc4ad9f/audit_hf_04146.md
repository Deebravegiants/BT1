# [M] `Curves::_buyCurvesToken`

## Summary
Severity: Medium
Contest weight: 0.1269
Dataset id: 20627
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the `buyCurvesToken()`, the logic check for the `msg.value` to be greater than `price + fees`. This is fine, since if the price moves after the estimates was provided to the user, the above validation checks if the funds received are sufficient to proceed with the transaction.

But, at the same time, it is equally important to refund any excess eth received which is not being done.

## Proof of Concept
Refer to the below code where the validation ensures that `msg.value` is not less than `price + total` fee.
    
       if (msg.value < price + totalFee) revert InsufficientPayment();

But, incase any additional funds were received, the same should be returned back to the caller.

## Recommendation
`uint256 excess = msg.value - (price + totalFee)`; if excess `> 0`, refund the amount back to the caller.

Valid but not high severity. Friend tech does not refund in fact.
