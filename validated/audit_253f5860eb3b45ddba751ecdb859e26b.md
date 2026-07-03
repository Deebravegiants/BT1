Audit Report

## Title
`LRTDepositPool.getAssetCurrentLimit()` Does Not Account for rsETH Daily Mint Cap, Returning Misleading Deposit Headroom - (File: contracts/LRTDepositPool.sol)

## Summary

`LRTDepositPool.getAssetCurrentLimit()` only checks the per-asset `depositLimitByAsset` cap but ignores the independent `maxMintAmountPerDay` daily mint cap enforced in `RSETH.mint()` via the `checkDailyMintLimit` modifier. When the daily rsETH quota is exhausted, the function returns a large positive headroom value while any actual deposit call will revert with `DailyMintLimitExceeded`. This causes the function to fail its core promise of reporting accurate deposit capacity.

## Finding Description

`getAssetCurrentLimit()` computes headroom solely from the per-asset deposit limit:

```solidity
// contracts/LRTDepositPool.sol L402-409
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
        return 0;
    }
    return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
}
```

The actual deposit execution path is: `depositAsset()` / `depositETH()` → `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` (checks only `depositLimitByAsset`) → `_mintRsETH()` → `RSETH.mint()`. The final step applies the `checkDailyMintLimit` modifier:

```solidity
// contracts/RSETH.sol L50-52
if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
    revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
}
```

`RSETH` exposes `remainingDailyMintLimit()` (L265-272) which correctly accounts for period resets, but `getAssetCurrentLimit()` never consults it. The two caps are entirely independent; exhausting one does not affect the other's reported value.

## Impact Explanation

The function `getAssetCurrentLimit()` is the canonical on-chain view for deposit capacity. When the daily rsETH quota is exhausted, it returns a materially incorrect positive value while every deposit call reverts. This is a concrete instance of **Low — Contract fails to deliver promised returns, but doesn't lose value**: integrators and smart contract routers acting on the return value will have their transactions revert, but no funds are permanently lost.

## Likelihood Explanation

`maxMintAmountPerDay` is an active operational control. During high-demand periods or after a single large institutional deposit, the daily quota can be fully consumed within a 24-hour window. Any integrator polling `getAssetCurrentLimit()` during the remainder of that window receives a misleading answer. The condition is routine, predictable, and requires no privileged access or attacker action to trigger — it arises from normal protocol usage.

## Recommendation

`getAssetCurrentLimit()` should incorporate the remaining rsETH daily mint headroom. The actual view function to call is `remainingDailyMintLimit()` (not `getRemainingMintableAmount()` as cited in the report — that function does not exist in the codebase):

```solidity
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
        return 0;
    }
    uint256 assetHeadroom = lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;

    address rsethToken = lrtConfig.rsETH();
    uint256 rsethHeadroom = IRSETH(rsethToken).remainingDailyMintLimit();
    uint256 rsethHeadroomInAsset = convertRsETHToAsset(asset, rsethHeadroom);

    return assetHeadroom < rsethHeadroomInAsset ? assetHeadroom : rsethHeadroomInAsset;
}
```

## Proof of Concept

1. Set `depositLimitByAsset[stETH] = 10_000e18`, `getTotalAssetDeposits(stETH) = 1_000e18`, `maxMintAmountPerDay = 500e18`.
2. A prior deposit in the same 24-hour window mints 500 rsETH, exhausting the daily quota. `RSETH.remainingDailyMintLimit()` returns `0`.
3. Call `getAssetCurrentLimit(stETH)` → returns `9_000e18` (ignores daily cap).
4. Submit `depositAsset(stETH, 1e18, 0)` → reaches `RSETH.mint()` → `checkDailyMintLimit` reverts with `DailyMintLimitExceeded(500e18, 500e18)`.
5. The integrator's transaction fails despite `getAssetCurrentLimit()` reporting ample capacity.

Foundry test plan: fork mainnet or deploy locally, call `mint` on RSETH to exhaust `maxMintAmountPerDay`, then assert `getAssetCurrentLimit(asset) > 0` while `depositAsset(asset, smallAmount, 0)` reverts.