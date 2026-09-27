# [M] `MAX_SLIPPAGE` Is Hardcoded To `1%`, Which Will Cause Issue During Market Volatility.

## Summary
Severity: Medium
Reporter: 0xhacksmithh
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L54
Type: audit-issue

## Details
# `MAX_SLIPPAGE` Is Hardcoded To `1%`, Which Will Cause Issue During Market Volatility.

## Summary
Refer  Vulnerability Detail

## Vulnerability Detail
`MAX_SLIPPAGE` is hardcoded to 1% in contract file `DCA.vy` and its a constant variable.
Which will cause issue, when market volatile and low liquidity
In those cases `Slippage` could go beyound `1%`, So Users Fund will get stucked.

```solidity
MAX_SLIPPAGE: constant(uint256) = 10000
```

## Impact
Refer  Vulnerability Detail

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L54

## Tool used

Manual Review

## Recommendation
Should be a changeable parameter depending upon situations, to allow users to get out.
