# [M] In case `amount < maxAmount` the protocol will return one USDC to the trader

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/105
Type: sherlock-finding

## Details
Ch_301

medium

# In case `amount < maxAmount` the protocol will return one USDC to the trader

## Summary
In case `amount < maxAmount` no need to recalculate the `_fees()`
 
## Vulnerability Detail
On `BufferBinaryOptions.checkParams()`
```solidity
        if (amount > maxAmount || newFee < optionParams.totalFee) {
            require(optionParams.allowPartialFill, "O29");
            amount = min(amount, maxAmount);
            (revisedFee, , ) = _fees(amount, settlementFeePercentage);
        } else {
            revisedFee = optionParams.totalFee;
        }
```
in case `amount < maxAmount` and `newFee < optionParams.totalFee` the user will lose (the **BufferRouter.sol** will return it back to the user) always 1 USDC because the recalculate of the `_fees()`

## Impact
In case `amount < maxAmount` and `newFee < optionParams.totalFee` the protocol will return back to the trader one USDC
So if the trader tries to trade 100 USDC with `sf` 20%, even if the ` 160 < maxAmount`. the user will only trade 99 USDC 

## Code Snippet
```solidity
       function checkParams(OptionParams calldata optionParams)
        external
        view
        override
        returns (
            uint256 amount,
            uint256 revisedFee,
            bool isReferralValid
        )
    {
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/105_
