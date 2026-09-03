# [M] [Tomo-M5] Transfer zero amount can be reverted

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/66
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M5] Transfer zero amount can be reverted

## Summary

Transfer zero amount can be reverted

## Vulnerability Detail

> Some tokens (e.g. `LEND`) revert when transfering a zero value amount.
> 
> 
> example: [RevertZero.sol](https://github.com/d-xo/weird-erc20/blob/main/src/RevertZero.sol)
> 

Ref: [https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers](https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers)

If the implementation is not designed for such errors, the user will not know the cause of the error.

In the `externalSwap` has no checking the `minReturnAmount` is greater than 0 in spite of the `dodoMutiswap()` and `mixSwap()` has this checking.

Therefore, this case can be happened in the `externalSwap()`

Also, this project assume the any ERC20 so this issue does matter for this project.

```
ERC20: any
ERC721: none
```

Ref: [https://github.com/sherlock-audit/2022-11-dodo-Tomosuke0930#on-chain-context](https://github.com/sherlock-audit/2022-11-dodo-Tomosuke0930#on-chain-context)

## Code Snippet

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L177](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L177)

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/66_
