# [H] Griefing attack can block Sense withdrawal altogether

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/204
Type: sherlock-finding

## Details
hyh

high

# Griefing attack can block Sense withdrawal altogether

## Summary

As Sense redeem() version operates Lender's balance, i.e. calls Sense's divider with the amount equal to lender's balance of Sense PTs, while Sense's adapter is user supplied, a griefing attack is possible by calling redeem() with fake precooked adapter that answer all the performed requests without reverting, but doesn't do anything else (i.e. no real operations, just noops without reverting).

The result of that is no Sense PT redeem is then possible with all current system supply of `IMarketPlace(marketPlace).token(u, m, p)` to be frozen on Redeemer's balance.

## Vulnerability Detail

Sense version of Redeemer's redeem() can be called with fake Sense's adapter `a`, that comply to the interface, provides `divider`, but do nothing else, so redeem() completes successfully. The result will be freeze of the total Sense PT system holdings for that maturity and underlying.

The reason is that redeem() requests specifically lender's balance to be redeemed by `divider`, but after the attack such balance will be empty, all the PTs be moved to Redeemer, and there is no logic to access them there.

This way subsequent redeem() calls with a correct Sense adapter will yield nothing, and Sense PTs previously retrieved are stuck with Redeemer as there are no other ways to redeem them apart Sense version redeem() that operates lender's balance only.

## Impact

User funds will be permanently frozen as underlying cannot be retrieved from Sense's PTs held on Redeemer's balance. There are no prerequisites for the attack, all is needed is system using Sense PTs at any substantial scale.

This is a violation of system core logic leading to permanent and massive fund freeze with no external assumptions, that is cheap to perform as no funds apart from cumulative gas cost are needed from an attacker, so setting the severity to be high.

## Code Snippet

Sense redeem() calls `SenseDivider` with `amount` equal to lender's balance, which is transferred to Redeemer:

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Redeemer.sol#L335-L373

```solidity
    /// @notice redeem method signature for Sense
    /// @param p principal value according to the MarketPlace's Principals Enum
    /// @param u address of an underlying asset
    /// @param m maturity (timestamp) of the market
    /// @param s Sense's maturity is needed to extract the pt address
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/204_
