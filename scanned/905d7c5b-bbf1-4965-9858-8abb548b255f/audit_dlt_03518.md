# [M] Fee on transfer tokens will not behave as expected

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-01-timeswap
Published: 2023-01-27
Source: https://github.com/code-423n4/2023-01-timeswap-findings/issues/247
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-timeswap/blob/main/packages/v2-option/src/TimeswapV2Option.sol#L145-L148
https://github.com/code-423n4/2023-01-timeswap/blob/main/packages/v2-option/src/TimeswapV2Option.sol#L235


# Vulnerability details

## Impact
According to [Whitepaper 1.1 Permissionless](https://github.com/code-423n4/2023-01-timeswap/blob/main/whitepaper.pdf):

"In Timeswap, liquidity providers can create pools for any ERC20 pair, without permission. It is designed to be generalized and works
for any pair of tokens, at any time frame, and at any market state ...

If fee on transfer token(s) is/are entailed, it will specifically make `mint()` and `swap()` revert in TimeswapV2Option.sol when checking if the token0 or token1 balance target is achieved.

## Proof of Concept
[File: TimeswapV2Option.sol#L144-L148](https://github.com/code-423n4/2023-01-timeswap/blob/main/packages/v2-option/src/TimeswapV2Option.sol#L144-L148)

```solidity
        // check if the token0 balance target is achieved.
        if (token0AndLong0Amount != 0) Error.checkEnough(IERC20(token0).balanceOf(address(this)), currentProcess.balance0Target);

        // check if the token1 balance target is achieved.
        if (token1AndLong1Amount != 0) Error.checkEnough(IERC20(token1).balanceOf(address(this)), currentProcess.balance1Target);
```
[File: TimeswapV2Option.sol#L234-L235](https://github.com/code-423n4/2023-01-timeswap/blob/main/packages/v2-option/src/TimeswapV2Option.sol#L234-L235)

```solidity
        // check if the token0 or token1 balance target is achieved.
        Error.checkEnough(IERC20(param.isLong0ToLong1 ? token1 : token0).balanceOf(address(this)), param.isLong0ToLong1 ? currentProcess.balance1Target : currentProcess.balance0Target);
```
[File: Error.sol#L148-L153](https://github.com/code-423n4/2023-01-timeswap/blob/main/packages/v2-library/src/Error.sol#L148-L153)

```solidity
    /// @dev Reverts when token amount not received.
    /// @param balance The balance amount being subtracted.
    /// @param balanceTarget The amount target.
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-timeswap-findings/issues/247_
