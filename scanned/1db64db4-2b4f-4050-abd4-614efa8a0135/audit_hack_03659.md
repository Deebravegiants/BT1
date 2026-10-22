# [H] FeeBuyback.submit ERC20 return values not checked

## Summary
Severity: High
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L62
Type: audit-issue

## Details
# FeeBuyback.submit ERC20 return values not checked

## Summary

## Vulnerability Detail
Some tokens (like USDT) don't correctly implement the EIP20 standard and their transfer/transferFrom function return void instead of a successful boolean. Calling these functions with the correct EIP20 function signatures will always revert.

## Impact
Tokens that don't correctly implement the latest EIP20 spec, like USDT, will be unusable in the protocol as they revert the transaction because of the missing return value. As there is a cToken with USDT as the underlying issue directly applies to the protocol.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L62

               '_telcoin.transferFrom(_safe, address(this), amount);'

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71

                'IERC20(token).transferFrom(_safe, address(this), amount);'

## Tool used

Manual Review

## Recommendation
We recommend using OpenZeppelin’s SafeERC20 versions with the safeTransfer and safeTransferFrom functions that handle the return value check as well as non-standard-compliant tokens.
