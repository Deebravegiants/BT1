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

    // update osToken position
    position.shares -= SafeCast.toUint128(osTokenShares);
    _positions[owner] = position;
```

2. Burn shares from the staker's position:

[VaultOsToken.sol#L235-L236](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L235-L236)

```solidity
    // burn owner shares
    _burnShares(owner, sharesToBurn);
```

3. Transfer the liquidated amount and bonus to the caller:

[VaultOsToken.sol#L247-L248](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L247-L248)

```solidity
    // transfer assets to the receiver
    _transferVaultAssets(receiver, receivedAssets);
```

As the entire liquidated amount and premium is transferred to the caller, the liquidation penalty is only reflected in `position.shares`. 

Therefore, if a position's LTV is more than 100% and the staker wants to fully exit his position, he is incentivised to fully liquidate himself instead of burning osETH using [`burnOsToken()`](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/modules/VaultOsToken.sol#L96-L112).

In the long term, this will be harmful to the osETH peg as it accrues bad debt for the protocol.

## Attack Scenario

For convenience, we assume that the shares to assets ratio the `osToken` contract and a vault is 1. 

Assume that Alice has the following osETH position in a vault:
- In the vault, she has `111e18` shares, which corresponds to 111 ETH staked.
- She holds `100e18` osETH, which corresponds to 100 ETH worth of osETH.
- Her current LTV is 90%.

The vault experiences a loss of 11 ETH:
- As the Alice is the only staker is the vault, all losses are accrued to her position.
- She now has 100 ETH staked, but holds 100 ETH worth of osETH.
- Therefore, her LTV ratio is now 100%.

Alice wishes to fully exit her position. If she calls `burnOsToken()` to burn all her shares and `redeem()` afterwards:
- `burnOsToken()` burns `100e18` osETH, which is all the osETH she has.
- `redeem()` burns `111e18` shares and transfers 100 ETH back to her. 

However, she can also choose to liquidate herself:
- She calls `liquidateOsToken()` with `osTokenShares = 99e18`:
  - `position.shares = 100e18 - 99e18 = 1e18`
  - The liquidation premium is 1%, hence `receivedAssets = 99e18 * 10100 / 100 = 100e18`
  - All her shares are burnt and 100 ETH is tranferred to her.
- However, as the liquidation only costs `99e18` osETH, she still has `1e18` osETH remaining.

As shown above, due to the liquidation premium, it is more profitable for Alice to self-liquidate instead of burning osETH to withdraw all her staked ETH. The additional `1e18` osETH she gained will accrue as bad debt to the protocol, which could harm the osETH peg in the long term.

## Impact

Due to the liquidation premium, stakers can gain additional osETH when exiting positions with greater than 100% LTV ratios. This additional osETH is accrued as bad debt for the protocol, which could accumulate and destabilize the osETH peg in the long term.

## Recommended Mitigation

Consider charging an additional liquidation fee alongside the premium, which is taken from the staker and given to the protocol. This could help to stabilize the osETH peg and discourage self-liquidation, as the staker would not get all his staked ETH in return when liquidating. 

Alternatively, consider removing the liquidation premium altogether.
