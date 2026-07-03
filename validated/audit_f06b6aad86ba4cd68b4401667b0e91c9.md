Audit Report

## Title
`getAssetCurrentLimit()` Overstates Actual Deposit Capacity by Ignoring `RSETH.maxMintAmountPerDay` - (File: contracts/LRTDepositPool.sol)

## Summary

`LRTDepositPool.getAssetCurrentLimit()` returns available deposit capacity based solely on the per-asset cumulative ceiling in `LRTConfig`, but the actual deposit execution path calls `RSETH.mint()`, which enforces an independent daily mint cap via the `checkDailyMintLimit` modifier. When the daily cap is exhausted, `getAssetCurrentLimit()` still returns a non-zero value, yet any deposit attempt reverts with `DailyMintLimitExceeded`. No funds are lost, but the view function fails to deliver its promised return.

## Finding Description

`getAssetCurrentLimit()` at [1](#0-0)  computes available capacity by subtracting cumulative deposits from `lrtConfig.depositLimitByAsset(asset)`. It has no awareness of `RSETH.maxMintAmountPerDay` or `RSETH.currentPeriodMintedAmount`.

The deposit execution path is:

1. `depositAsset()` / `depositETH()` → `_beforeDeposit()` at [2](#0-1)  — checks only `_checkIfDepositAmountExceedesCurrentLimit()`, which mirrors the same per-asset cap logic as `getAssetCurrentLimit()`.
2. `_mintRsETH()` at [3](#0-2)  — calls `IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint)`.
3. `RSETH.mint()` applies the `checkDailyMintLimit` modifier at [4](#0-3) , which reverts with `DailyMintLimitExceeded` if `currentPeriodMintedAmount + amount > maxMintAmountPerDay`.

The two limits are orthogonal: the per-asset cap is a cumulative lifetime ceiling; the daily mint cap resets every 24 hours and is enforced at the token level. `getAssetCurrentLimit()` only accounts for the former.

## Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.** Any user or off-chain integrator relying on `getAssetCurrentLimit()` to determine safe deposit amounts will receive an inflated answer whenever the RSETH daily mint cap is exhausted. A subsequent deposit of that amount reverts cleanly with `DailyMintLimitExceeded`; no funds are lost or locked.

## Likelihood Explanation

`maxMintAmountPerDay` is an active, manager-configured parameter (`setMaxMintAmountPerDay`). During periods of high deposit activity — exactly when integrators are most likely to query `getAssetCurrentLimit()` — the daily cap is most likely to be exhausted. The mismatch is reachable under normal operating conditions by any unprivileged depositor without any special preconditions beyond the daily cap being near its limit.

## Recommendation

`getAssetCurrentLimit()` should cap its return value by the remaining RSETH daily mint capacity, converted to asset units:

1. Call `RSETH.remainingDailyMintLimit()` (already implemented at [5](#0-4) ).
2. Convert the remaining rsETH headroom to asset units using `LRTOracle.rsETHPrice()` and `LRTOracle.getAssetPrice(asset)`.
3. Return `min(per-asset cap remainder, converted daily mint headroom)`.

## Proof of Concept

1. `maxMintAmountPerDay` = 100 rsETH; `currentPeriodMintedAmount` = 99 rsETH.
2. `getAssetCurrentLimit(ETH)` returns 500 ETH (per-asset cap has ample room).
3. User calls `getAssetCurrentLimit(ETH)`, receives 500 ETH, and submits a deposit of 10 ETH (≈9.5 rsETH to mint).
4. `_beforeDeposit` passes — 10 ETH is within the per-asset cap.
5. `_mintRsETH` calls `RSETH.mint(user, 9.5e18)`.
6. `checkDailyMintLimit`: `99e18 + 9.5e18 = 108.5e18 > 100e18` → reverts with `DailyMintLimitExceeded`.
7. The user's transaction reverts despite `getAssetCurrentLimit()` advertising 500 ETH of available capacity.

### Citations

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```

**File:** contracts/RSETH.sol (L42-56)
```text
    modifier checkDailyMintLimit(uint256 amount) {
        // Check if we need to reset the period if it has been more than 24 hours
        if (block.timestamp >= periodStartTime + 1 days) {
            currentPeriodMintedAmount = 0;
            periodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }

        currentPeriodMintedAmount += amount;
        _;
    }
```

**File:** contracts/RSETH.sol (L265-272)
```text
    function remainingDailyMintLimit() external view returns (uint256) {
        if (maxMintAmountPerDay == 0) return 0;

        // If we're on a new day but no mint has occurred yet, treat currentPeriodMintedAmount as 0
        uint256 effectiveDailyMintAmount = (block.timestamp >= periodStartTime + 1 days) ? 0 : currentPeriodMintedAmount;

        return maxMintAmountPerDay > effectiveDailyMintAmount ? maxMintAmountPerDay - effectiveDailyMintAmount : 0;
    }
```
