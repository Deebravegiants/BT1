# [M] Wrong `routeFeeRate` value, users have to pay more fee

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/93
Type: sherlock-finding

## Details
minhquanym

medium

# Wrong `routeFeeRate` value, users have to pay more fee

## Summary
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L57-L58

## Vulnerability Detail

The `routeFeeRate` is wrong. The comment above said that `routeFeeRate` should be 0.015%.
However
```python
1500000000000000 / 1e18 * 100% = 0.15%
```

## Impact
The `routeFeeRate` value is higher than expected, so users have to pay more fee.

## Code Snippet
```solidity
// dodo route fee rate, unit is 10**18, default fee rate is 1.5 * 1e15 / 1e18 = 0.0015 = 0.015%
uint256 public routeFeeRate = 1500000000000000; // @audit wrong rate, it's 0.15% instead of 0.015%
// dodo route fee receiver
address public routeFeeReceiver;
```

## Tool used

Manual Review

## Recommendation

Consider decreasing `routeFeeRate` from `1500000000000000` to `150000000000000`
