# [M] Yield sources cannot be swapped back

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-07-pooltogether
Published: 2021-07-31
Source: https://github.com/code-423n4/2021-07-pooltogether-findings/issues/51
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

The `_setYieldSource` function of `SwappableYieldSource` calls the `safeApprove` function to approve the yield sources with the maximum allowance of transferring underlying tokens. However, according to OpenZeppelin's implementation, the `safeApprove` function succeeds only if the current allowance is zero or the allowance to be set is zero (see the following link).

As a result, a yield source cannot be set twice by the contract. For example, set A -> set B -> set A is not possible since A's allowance is non-zero in the second "set A", causing the transaction to revert.

## Proof of Concept

Referenced code:
[SwappableYieldSource.sol#L259](https://github.com/pooltogether/swappable-yield-source/blob/89cf66a3e3f8df24a082e1cd0a0e80d08953049c/contracts/SwappableYieldSource.sol#L259)

[OpenZeppelin - SafeERC20.sol#L52-L55](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol#L52-L55)

## Recommended Mitigation Steps

Use `safeIncreaseAllowance` to increase the allowance to the maximum instead.
