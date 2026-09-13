# [H] FeeBuy.rescueERC20 backdoes not work on non-standard compliant tokens like USDT

## Summary
Severity: High
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95
Type: audit-issue

## Details
# FeeBuy.rescueERC20 backdoes not work on non-standard compliant tokens like USDT

## Summary

## Vulnerability Detail
The `FeeBuy.rescueERC20`  function uses the standard IERC20 function for the transfer call and proceeds with a `checkReturnCode` function to handle non-standard compliant tokens that don't return a return value. However, this does not work as a calling 'IERC20(externalToken).transfer(account, amount);' already reverts if the token does not return a return value, as token's IERC20.transfer is defined to always return a boolean.

## Impact
When using any non-standard compliant token like USDT, the function will revert. Deposits for these tokens are broken, which is bad as USDT is a valid underlying for the cUSDT cToken.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95

           'IERC20(externalToken).transfer(account, amount);'

## Tool used

Manual Review

## Recommendation
We recommend using OpenZeppelin’s [SafeERC20](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v4.1/contracts/token/ERC20/utils/SafeERC20.sol#L74) versions with the safeApprove function that handles the return value check as well as non-standard-compliant tokens.
