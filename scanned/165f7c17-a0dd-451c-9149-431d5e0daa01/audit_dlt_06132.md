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
    uint256 sharesToBurn = convertToShares(receivedAssets);
```

[VaultOsToken.sol#L235-L236](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L235-L236)

```solidity
    // burn owner shares
    _burnShares(owner, sharesToBurn);
```

4. Transfer the liquidated amount to the caller:

[VaultOsToken.sol#L247-L248](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L247-L248)

```solidity
    // transfer assets to the receiver
    _transferVaultAssets(receiver, receivedAssets);
```

As seen from above, the amount of assets liquidated is determined using the osETH exchange rate. Additionally, 
since the entire liquidated amount and premium is transferred to the caller, the liquidation penalty is only reflected in `position.shares`. 

This becomes an issue if:

1. A position's LTV is greater than 100%
2. The staker wants to fully exit his position

as he is incentivised to fully liquidate himself instead of burning osETH using [`burnOsToken()`](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L96-L112). This way, the staker only needs to use a portion of his osETH balance to withdraw all his staked ETH.

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

Alice wants to fully exit her position and withdraw all her staked ETH. If she calls `burnOsToken()` to burn all her shares and `redeem()` afterwards:
- She calls `burnOsToken()` with all her osETH, as `position.shares` must be 0 for a staker to withdraw his entire balance.
- `redeem()` burns `32e18` shares and transfers 28 ETH to Alice.

However, if she liquidates her own position, she gets to keep a portion of her osETH:
- She calls `liquidateOsToken()` with `osTokenShares = 28e18`:
  - `position.shares = 28.8e18 - 28e18 = 0.8e18`
  - Since osETH's exchange rate is 1 and the liquidation premium is 0%, `receivedAssets = 28e18`
  - Therefore, all her shares are burnt and 28 ETH is transferred to her.

Although `position.shares` is non-zero, Alice has managed to withdraw all her staked ETH by self-liquidating. By doing so, she also gained an additional `0.8e18` osETH.

## Impact

By self-liquidating, stakers can gain additional osETH when exiting positions with greater than 100% LTV ratios. The additional osETH is accrued as bad debt for the protocol, which could accumulate and destabilize the osETH peg in the long term.

## Recommended Mitigation

Consider charging an additional liquidation fee, which is taken from the staker and given to the protocol. This would discourage self-liquidation as the staker does not get all his staked ETH in return when liquidating his own position.
