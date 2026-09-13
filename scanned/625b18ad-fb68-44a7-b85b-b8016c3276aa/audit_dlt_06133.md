# [M] Liquidation doesn't make osETH positions healthier when LTV >= 100%

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-26
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/111
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

As seen from above, the amount of shares removed from the user's osETH position and vault shares are equal in assets. 

However, this only makes the user's position healthier if its LTV was below 100% before liquidation. If a the position has a LTV ratio above 100%, its LTV will actually increase, causing the position to become unhealthier after liquidation.

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

A user calls `liquidateOsToken()` with `osTokenShares = 10e18` to liquidate Alice's position:
- `position.shares = 28.8e18 - 10e18 = 18.8e18`
- As the liquidation premium is 0%, `receivedAssets = 10e18`
- Therefore, 10 ETH is tranferred from Alice's stake to the liquidator.

After the liquidation, Alice's position has become unhealthier:
- She has 18 remaining ETH staked in the vault.
- She holds `18.8e18` osETH, which corresponds to 18.8 ETH.
- Therefore, her LTV ratio is now 104.4%, which is more than before liquidation.

## Impact

When positions are liquidated, they are meant to become healthier. However, the current liquidation mechanism makes positions with a LTV ratio of above 100% become unhealthier instead, which would be harmful to the staker.

## Recommended Mitigation

Consider implementing a separate liquidation mechanism for positions above 100% LTV that reduces `position.shares` by a larger percentage, which would make it healthier.
