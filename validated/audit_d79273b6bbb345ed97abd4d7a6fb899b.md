Audit Report

## Title
Stale `rsETHPrice` in `instantWithdrawal` causes users to receive fewer assets than fair value — (`contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTWithdrawalManager.instantWithdrawal` computes the asset payout via `getExpectedAssetAmount`, which reads `LRTOracle.rsETHPrice` — a stored state variable updated only on explicit calls to `updateRSETHPrice()` or `updateRSETHPriceAsManager()`. When yield accrues and the stored price lags behind the true price, users burn rsETH at the stale (lower) rate and receive fewer underlying assets than their rsETH is currently worth. Unlike `unlockQueue`, `instantWithdrawal` has no caller-supplied price-bounds guard to protect against this.

## Finding Description
`LRTOracle.rsETHPrice` is a plain storage variable set only inside `_updateRsETHPrice()`. [1](#0-0) 

`getExpectedAssetAmount` reads this stored value directly: [2](#0-1) 

`instantWithdrawal` calls `getExpectedAssetAmount` and immediately burns the user's rsETH with no freshness check: [3](#0-2) 

`unlockQueue`, by contrast, passes caller-supplied `minimumRsEthPrice` / `maximumRsEthPrice` bounds to `_validatePrices` before processing: [4](#0-3) 

A critical aggravating factor: `updateRSETHPrice()` is public but will revert for unprivileged callers when the price increase exceeds `pricePercentageLimit`: [5](#0-4) 

This means that in the exact scenario where the price gap is largest — after significant yield accrual above the configured threshold — a regular user calling `updateRSETHPrice()` to self-protect will receive `PriceAboveDailyThreshold`. They are forced to proceed with the stale price or not withdraw at all. Only a manager can call `updateRSETHPriceAsManager()` to refresh the price in that window. [6](#0-5) 

## Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The user burns rsETH worth `X * truePrice` ETH but receives assets worth only `X * stalePrice` ETH. The shortfall remains in `LRTUnstakingVault`; no funds are stolen. The protocol fails to deliver the fair redemption value of the user's rsETH at the time of the call, which is a concrete instance of the allowed Low impact class.

## Likelihood Explanation
No privileged role or external compromise is required. The condition arises from normal protocol operation whenever yield accrues between oracle updates. The staleness window is determined by bot/operator update cadence. When the price gap exceeds `pricePercentageLimit`, unprivileged users cannot self-protect by calling `updateRSETHPrice()` — it reverts — making the condition non-self-serviceable for the users most affected. Any rsETH holder can trigger `instantWithdrawal` directly.

## Recommendation
Before computing `assetAmountUnlocked` in `instantWithdrawal`, either:
1. Call `_updateRsETHPrice()` internally (or `updateRSETHPrice()` if the caller is trusted) to ensure the price is fresh before the burn; or
2. Add caller-supplied `minimumRsEthPrice` / `maximumRsEthPrice` parameters mirroring the `unlockQueue` pattern, so users can set a floor on the price at which they are willing to redeem and the transaction reverts if the stored price is below their acceptable minimum.

## Proof of Concept
```solidity
// Fork test sketch (no mainnet execution)
// 1. Fork mainnet; advance time so yield accrues but updateRSETHPrice() is NOT called.
//    rsETHPrice stored = 1.00e18; true price (if updated) = 1.05e18.
//    If pricePercentageLimit is set below 5%, updateRSETHPrice() reverts for non-managers.
// 2. User holds 1e18 rsETH; asset is stETH with assetPrice = 1e18.
// 3. User calls instantWithdrawal(stETH, 1e18, "").
//    assetAmountUnlocked = 1e18 * 1.00e18 / 1e18 = 1.00e18 stETH  (stale)
// 4. Manager calls updateRSETHPriceAsManager(); rsETHPrice becomes 1.05e18.
// 5. Fair payout would have been: 1e18 * 1.05e18 / 1e18 = 1.05e18 stETH.
// 6. User received 1.00e18 instead of 1.05e18 — shortfall of 0.05e18 stETH.
//    Invariant broken: assetAmountUnlocked < rsETHUnstaked * trueRsETHPrice / assetPrice.
//    The 0.05e18 stETH shortfall remains in LRTUnstakingVault.
```

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L260-265)
```text
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTWithdrawalManager.sol (L228-229)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L288-295)
```text
        _validatePrices(
            params.rsETHPrice,
            params.assetPrice,
            minimumRsEthPrice,
            maximumRsEthPrice,
            minimumAssetPrice,
            maximumAssetPrice
        );
```

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
