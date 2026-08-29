# [M] Liquidation premium encourages stakers to self-liquidate instead of burning osETH when LTV >= 100%

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-26
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/109
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0x2502a331733e483bfc74c72e55de7a09d937a69178150a7689623d11a3640543
**Severity:** medium

**Description:**
## Bug Description

In `VaultOsToken.sol`, when users call `liquidateOsToken()` to liquidate a staker with an unhealthy osETH position, they are given an additional percentage bonus on top of the the liquidated amount (known as the liquidation premium).

This behavior can be seen in `_redeemOsToken()`:

[VaultOsToken.sol#L186-L193](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L186-L193)

```solidity
    // calculate received assets
    if (isLiquidation) {
      receivedAssets = Math.mulDiv(
        _osToken.convertToAssets(osTokenShares),
        liqBonusPercent,
        _maxPercent
      );
    } else {
```

Where:
- `osTokenShares` is the amount of osToken shares to liquidate.
- `liqBonusPercent` is the liquidation premium.

The liquidation has the following effects:

1. Burns `osTokenShares` from the caller's osETH balance and staker's osETH position: 

[VaultOsToken.sol#L221-L226](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L221-L226)

```solidity
    // reduce osToken supply
    _osToken.burnShares(msg.sender, osTokenShares);

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/109_
