# [H] Frontrunning is infinitely profitable, slippage is implied 100%

## Summary
Severity: High
Chain: Smart contract
Component: 2021-07-spartan
Published: 2021-07-21
Source: https://github.com/code-423n4/2021-07-spartan-findings/issues/85
Type: code-finding

## Details
# Handle

tensors


# Vulnerability details

## Impact
There are no minimum amounts out, or checks that frontrunning/slippage is sufficiently mitigated.
This means that anyone with enough capital can force arbitrarily large slippage by sandwiching transactions, close to 100%. 

## Proof of Concept
https://github.com/code-423n4/2021-07-spartan/blob/e2555aab44d9760fdd640df9095b7235b70f035e/contracts/Pool.sol#L284

https://github.com/code-423n4/2021-07-spartan/blob/e2555aab44d9760fdd640df9095b7235b70f035e/contracts/Pool.sol#L296

## Recommended Mitigation Steps
Add a minimum amount out parameter. The function reverts if the minimum amount isn't obtained.
