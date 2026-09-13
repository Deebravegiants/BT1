# [H] 6.1 Permit2Lib Argument Casting

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

The functions permit2 and transferFrom2 of Permit2Lib both take uint256 amount as an
argument. The lib will first attempt to call the token directly and falls back to the call to Permit2 if it fails.
However, the Permit2.permit and Permit2.transferFrom take uint160 amount as an
argument. The initial uint256 amount will be cast to uint160 for that call. Assuming some contract A
relies on transferFrom2 for token transfers, the following can happen:

```
1.The user calls a function on A that attempts to pull funds from the user using transferFrom2. For
amount, the user specifies 2**170.
```
```
2.A direct call to token.transferFrom fails.
3.Permit2Lib falls back to Permit2.transferFrom with uint160(2**170) == 0 as an amount.
4.The call is successful. No value is actually transferred.
5.Contract A now thinks that 2**170 tokens were actually transferred.
```
Similar casting happens in the permit2 function.

Code corrected:

The SafeCast library is now used for casting to a uint160 before the Permit2 contract is called. The
casting of a value that is greater than type(uint160).max would revert now.
