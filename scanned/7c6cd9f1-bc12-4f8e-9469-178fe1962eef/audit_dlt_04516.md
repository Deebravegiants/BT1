# [H] The short side should also pay the funding fee

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/43
Type: sherlock-finding

## Details
WATCHPUG

high

# The short side should also pay the funding fee

## Summary

The current implementation will always charge the funding fees from the long side and wrongfully credit the funding fee to the short side when they should actually pay for it.

## Vulnerability Detail

Both `overbalancedFunding` and `underbalancedFunding` in `_calculateFundingAmount()` are `uint256`, so `fundingAmount[0]` will always be a negative number.

As a result, `_rebalancePoolsAndExecuteBatchedActions()` at L146-147, the short side will always be credited for the funding fee instead of paying for it.

## Impact

Wrong accounting of funding fees.

## Code Snippet

https://github.com/sherlock-audit/2022-11-float-capital/blob/main/contracts/market/template/MarketCore.sol#L41-L67

https://github.com/sherlock-audit/2022-11-float-capital/blob/main/contracts/market/template/MarketCore.sol#L118-L160

## Tool used

Manual Review

## Recommendation

Consider using uint256 for the `fundingAmount` for both sides:

```solidity
  function _calculateFundingAmount(
    uint256 overbalancedIndex,
    uint256 overbalancedValue,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/43_
