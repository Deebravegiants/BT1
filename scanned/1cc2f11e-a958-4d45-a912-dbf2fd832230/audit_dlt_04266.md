# [M] Redeem function for Sense finance does not check the maturity.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/146
Type: sherlock-finding

## Details
ctf_sec

medium

# Redeem function for Sense finance does not check the maturity.

## Summary

Redeem function for Sense finance does not check the maturity.

## Vulnerability Detail

In the redeem function implementation, the code uses a lengthy implementation but accurate implementation to
check if the position's maturity

If the position is not matured, the transaction revert before going to redeem:

```solidity
// Verify that the token has matured
if (maturity > block.timestamp) {
    revert Exception(7, maturity, 0, address(0), address(0));
}
```

However, the checking for maturity is missing in Sense redeeming function!

## Impact

Redeeming before maturity should not be allowed.

## Code Snippet

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Redeemer.sol#L335-L365

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Redeemer.sol#L254-L259

## Tool used


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/146_
