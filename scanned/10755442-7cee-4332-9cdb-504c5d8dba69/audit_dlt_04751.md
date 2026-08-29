# [H] Underflow in `_previewWithdraw()` causing DoS

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/84
Type: sherlock-finding

## Details
__141345__

medium

# Underflow in `_previewWithdraw()` causing DoS


## Summary

In `_previewWithdraw()`, the `totalContractsSold` could grow larger than `auction.totalContracts` before the buyer's order is reached. Then the underflow will revert, `withdraw()` function will not work, user funds will be locked.


## Vulnerability Detail

If the orders before the current buyer add up above `auction.totalContracts`, in the if block:
```solidity
    uint256 remainder =
        auction.totalContracts - totalContractsSold;
```
will revert due to underflow.


## Impact

- `withdraw()` function could fail due to DoS.
- User funds could get locked temporarily or forever.


## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L317-L318


https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L343


## Tool used


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/84_
