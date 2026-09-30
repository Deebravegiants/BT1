# [H] amountOutMinimum on UniV3SwapInput not set slippage could be frontrun

## Summary
Severity: High
Reporter: Fanz
Source: https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L237
Type: audit-issue

## Details
# amountOutMinimum on UniV3SwapInput not set slippage could be frontrun

## Summary
amountOutMinimum on UniV3SwapInput not set slippage could be frontrun

## Vulnerability Detail
Currently amountOutMinimum always 0 mean accept any prices, could be got front run

## Impact
Protocol losing funds

## Code Snippet
https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L237
## Tool used

Manual Review

## Recommendation
Set slippage
