# [M] `sharesToTokenAmount`: Division by zero

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-03-biconomy
Published: 2022-03-15
Source: https://github.com/code-423n4/2022-03-biconomy-findings/issues/53
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-03-biconomy/blob/db8a1fdddd02e8cc209a4c73ffbb3de210e4a81a/contracts/hyphen/LiquidityProviders.sol#L192


# Vulnerability details

## Impact
The public `sharesToTokenAmount` function does not check if the denominator `totalSharesMinted[_tokenAddress]` is zero.
Neither do the callers of this function. The function will revert.
Calling functions like `getFeeAccumulatedOnNft` and `sharesToTokenAmount` from another contract should never revert.

## Recommended Mitigation Steps
Return 0 in case `totalSharesMinted[_tokenAddress]` is zero.
