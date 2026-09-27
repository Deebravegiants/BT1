# [M] secRewardsPerShare Insufficient precision

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2024-01-canto/blob/5e0d6f1f981993f83d0db862bcf1b2a49bb6ff50/src/LendingLedger.sol#L71
Type: audit-issue

## Details
# Lines of code

https://github.com/code-423n4/2024-01-canto/blob/5e0d6f1f981993f83d0db862bcf1b2a49bb6ff50/src/LendingLedger.sol#L71


# Vulnerability details

## Vulnerability details
>we also introduced the field secRewardDebt. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

the current calculation formula for `secRewardsPerShare` is as follows:
```solidity
market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply);
```
`marketSupply` is `cNOTE`, with a precision of `1e18`
So as long as the supply is greater than `1` cNote, `secRewardsPerShare` is easily `rounded down` to `0`
Example:
marketSupply = 10e18
blockDelta = 1
secRewardsPerShare=1 *  1e18 / 10e18 = 0

## Impact
Due to insufficient precision, `secRewardsPerShare` will basically be 0
## Recommended Mitigation
It is recommended to use 1e27 for `secRewardsPerShare`
```solidity
    market.secRewardsPerShare += uint128((blockDelta * 1e27) / marketSupply);
```


## Assessed type

Decimal
