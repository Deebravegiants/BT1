# [H] Manual deposits can manipulate share price

## Summary
Severity: High
Chain: Smart contract
Component: 2021-06-pooltogether
Published: 2021-06-24
Source: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/105
Type: code-finding

## Details
# Handle

tensors


# Vulnerability details

## Impact
Increasing/decreasing the balance of tokens in the pool by manually depositing them changes the values of the shares.

## Proof of Concept
https://github.com/pooltogether/aave-yield-source/blob/bc65c875f62235b7af55ede92231a495ba091a47/contracts/yield-source/ATokenYieldSource.sol#L147-L149

https://github.com/pooltogether/aave-yield-source/blob/bc65c875f62235b7af55ede92231a495ba091a47/contracts/yield-source/ATokenYieldSource.sol#L164-L166

Suppose that before I swap my shares (S in total ) for tokens (T in total) I deposit X tokens to the pool without getting shares for them.

By the shares to tokens formula, if S(A+X)/T -X > 0 I can take a profit from artificially increasing the price.

If I have some mechanism to withdraw the tokens X, that I deposited then it is always profitable to manipulate the price of the shares. I couldn't find such a mechanism in the code, but maybe someone else did. 

## Recommended Mitigation Steps
Record the price gained through interest alone, or don't allow deposits from unknown sources.
