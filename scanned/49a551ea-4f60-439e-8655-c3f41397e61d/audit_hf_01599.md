# [M] Approve race condition in ERC420.approve()

## Summary
Severity: Medium
Contest weight: 0.3902
Dataset id: 8583
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ERC420.approve() doesn't have any protection against the multiple withdrawal attack on the approve(), transferFrom() & safetTransferFrom functions. This race condition can occur when the owner calls approve() function to change the allowance of the spender on his tokens, but then the spender sandwiches the approve() transaction where he first frontruns it and calls transferFrom() before changing the allowance and the other transferFrom() call is made after the approve() transaction is made (that has changed the spender allowance); which will lead to the owner's tokens being spent twice by the spender.
Code Snippet
ERC420.approve function
```solidity
(bool) {
    _approve(owner, spender, value);
    return true;
}
```

## Recommendation
Add functions to increase/decrease allowance.
