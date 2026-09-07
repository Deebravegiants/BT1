# [H] Missing check in `ExchangeProxy.executeSwapDirect` lead to users potentially losing a significant amount of their assets

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/43
Type: sherlock-finding

## Details
seyni

high

# Missing check in `ExchangeProxy.executeSwapDirect` lead to users potentially losing a significant amount of their assets

## Summary
If `ExchangeProxy.executeSwapDirect` is called from `ExchangeProxy.executeSwap` users could lose a significant amount of value of their assets.
## Vulnerability Detail
When `ExchangeProxy.executeSwapDirect` is called from `ExchangeProxy.executeSwap`, there is no check to verify that the `amountReceived` hasn't considerably decreased compared to a fair amount, instead there is only a check for `amountReceived > 0`:
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L186
```solidity
        require(amountReceived > 0, "zero amount received");
```
The missing check is done in `HardenedTopupProxy` like this:
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L346
```solidity
        require(amountReceived >= _expectedMinimumReceived, "minimum swap amount not met");
```
But is never done if `ExchangeProxy.executeSwapDirect` is used through `ExchangeProxy.executeSwap`.

## Impact
When `ExchangeProxy.executeSwapDirect` is called from `ExchangeProxy.executeSwap`, a swap could go through with an user losing a significant amount of value of his assets.

## Code Snippet
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L186
```solidity
        require(amountReceived > 0, "zero amount received");
```

## Tool used

Manual Review

## Recommendation
The following check:
```solidity
        require(amountReceived >= _expectedMinimumReceived, "minimum swap amount not met");
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/43_
