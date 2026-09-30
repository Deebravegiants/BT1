# [M] SwapRouter contract uses transferFrom() instead of safeTransferFrom()

## Summary
Severity: Medium
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67
Type: audit-issue

## Details
# SwapRouter contract uses transferFrom() instead of safeTransferFrom()

## Summary
Contract is not using `safeTransferFrom` instead of `transferFrom` which could lead to several problems with the protocol.

## Vulnerability Detail
In the contract `SwapRouter.py`, the `transferFrom` is being used. Since the docs state that the Margin Dex should support tokens like USDT, and tokens like that don't follow the ERC20 standard, it could make some of the trades to fail (like in the case of using USDT).

## Impact
This issue will cause the transfers to fail without being noticed by the calling contract. The docs state that the margin dex will use OZ ERC20-compliant tokens but since they also plan to support tokens like USDT (which have a different behavior), the protocol should use `safeTransferFrom`.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67

## Tool used
Manual Review

## Recommendation
Replace `transferFrom` with the `safeTransferFrom` implementation.
