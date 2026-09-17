# [M] Stakers might continue accumulating staking fees after being fully liquidated

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-26
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/110
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
    uint256 sharesToBurn = convertToShares(receivedAssets);
```

[VaultOsToken.sol#L235-L236](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L235-L236)

```solidity
    // burn owner shares
    _burnShares(owner, sharesToBurn);
```

As seen from above, the amount of assets liquidated and shares burnt is calculated based on `osTokenShares`. As such, if the position's LTV is above 100%, it becomes possible for a staker's entire balance to be liquidated, but `position.shares` still has some shares remaining.

This is an issue as the fee charged on rewards accumulated by osETH, known as the staking fee, is calculated based on `position.shares`:

[VaultOsToken.sol#L68-L71](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L68-L71)

```solidity
    OsTokenPosition memory position = _positions[msg.sender];
    if (position.shares > 0) {
      _syncPositionFee(position);
    } else {
```

[VaultOsToken.sol#L255-L267](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L255-L267)

```solidity
  function _syncPositionFee(OsTokenPosition memory position) private view {
    // fetch current cumulative fee per share
    uint256 cumulativeFeePerShare = _osToken.cumulativeFeePerShare();

    // check whether fee is already up to date
    if (cumulativeFeePerShare == position.cumulativeFeePerShare) return;

    // add treasury fee to the position
    position.shares = SafeCast.toUint128(
      Math.mulDiv(position.shares, cumulativeFeePerShare, position.cumulativeFeePerShare)
    );
    position.cumulativeFeePerShare = SafeCast.toUint128(cumulativeFeePerShare);
  }
```

Therefore, after being fully liquidated, a staker might still continue to accumulate staking fees, unbeknownst to him. If he decides to re-stake in the vault after a long period of time, his `position.shares` might have grown quite big, limiting the amount of osETH he can mint and possibily making his new position unhealthy.

## Attack Scenario

For convenience, we assume that:
- The shares to assets ratio the `osToken` contract and a vault is 1. 
- The liquidation premium is 0%; `liqBonusPercent` is set to `10_000`.

Assume that Alice has the following osETH position in a vault:
- In the vault, she has `32e18` shares, which corresponds to 32 ETH staked.
- She holds `28.8e18` osETH, which corresponds to 28.8 ETH worth of osETH.
- Her current LTV is 90%.

The vault experiences a loss of 4 ETH:
- As the Alice is the only staker is the vault, all losses are accrued to her position.
- She now has 28 ETH staked, but holds 28.8 ETH worth of osETH.
- Therefore, her LTV ratio is now 103%.

A user calls `liquidateOsToken()` with `osTokenShares = 28e18` to liquidate Alice's position:
  - `position.shares = 28.8e18 - 28e18 = 0.8e18`
  - Since osETH's exchange rate is 1 and the liquidation premium is 0%, `receivedAssets = 28e18`
  - Therefore, all her shares are burnt and 28 ETH is transferred to the liquidator.

Since Alice has no more shares and ETH staked in the vault, she assumes that her position is healthy. However, as `position.shares` is still not zero, she continue to accumulate staking fees.

After a long duration (eg. 1 year), she decides to re-stake in the vault. However, when she calls `mintOsToken()`, `position.shares` becomes much larger than `0.8e18` due to the staking fee, significantly reducing the amount of osETH she is able to mint for her deposited ETH.

## Impact

When positions with LTV ratio above 100% are liquidated, `position.shares` is not reset, causing stakers to unfairly accumulate staking fees although they no longer have staked ETH in the vault. 

This could potentially cause a loss of osETH for stakers if they decide to re-stake in the vault after a long period of time.

## Recommended Mitigation

In `_redeemOsToken()`, consider resetting the staker's `position.shares` to 0 if they are fully liquidated:

[VaultOsToken.sol#L224-L228](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L224-L228)

```diff
-   // update osToken position
-   position.shares -= SafeCast.toUint128(osTokenShares);
-   _positions[owner] = position;

    uint256 sharesToBurn = convertToShares(receivedAssets);

+   if (sharesToBurn == _balances[owner]) {
+     position.shares = 0    
+   } else {
+     position.shares -= SafeCast.toUint128(osTokenShares);
+   }
+   _positions[owner] = position;
```
