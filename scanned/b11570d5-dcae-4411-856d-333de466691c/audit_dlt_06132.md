# [M] Staker are incentivised to self-liquidate instead of burning osETH when LTV >= 100%

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-26
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/112
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0xa2b2b9cfac0e8a5b2bb559c1ee365019a2d990b149d46c7711f76267701e2b49
**Severity:** medium

**Description:**
## Bug Description

In `VaultOsToken.sol`, when `liquidateOsToken()` is called to liquidate a staker, the following occurs:

1. The amount of assets liquidated is calculated based on `osTokenShares`:

[VaultOsToken.sol#L187-L193](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L187-L193)

```solidity
    if (isLiquidation) {
      receivedAssets = Math.mulDiv(
        _osToken.convertToAssets(osTokenShares),
        liqBonusPercent,
        _maxPercent
      );
    } else {
```

2. `osTokenShares` is subtracted from the staker's osETH position:

[VaultOsToken.sol#L224-L226](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L224-L226)

```solidity
    // update osToken position
    position.shares -= SafeCast.toUint128(osTokenShares);
    _positions[owner] = position;
```

3. A corresponding amount of shares is burned from the user's vault shares:

[VaultOsToken.sol#L228](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L228)

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/112_
