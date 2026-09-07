# [M] ERC20 function call return value not checked

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/78
Type: sherlock-finding

## Details
__141345__

medium

# ERC20 function call return value not checked

## Summary

Some ERC20 does not fully comply with the standard, such as USDT. The transferFrom doesn’t revert upon failure but returns false.

Even USDC could change, since it is upgradable. Deviate from the ERC20 standard is one possibility.


## Vulnerability Detail

In `submit()`, some erc20 function call return value is not checked and could potentially incur fund loss or DoS.


## Impact

Some fee could not be received and lost, the protocol and users both could be affected



## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71-L72



## Tool used

Manual Review

## Recommendation

Use the OpenZeppelin's transfer wrapper for token transfer.
