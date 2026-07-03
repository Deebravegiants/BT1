### Title
`getAssetCurrentLimit()` Overstates Actual Deposit Capacity by Ignoring `RSETH.maxMintAmountPerDay` - (File: contracts/LRTDepositPool.sol)

### Summary

`LRTDepositPool.getAssetCurrentLimit()` computes available deposit room using only the per-asset deposit cap stored in `LRTConfig`, but the actual deposit execution path calls `RSETH.mint()`, which enforces a separate, independent daily mint cap (`maxMintAmountPerDay`). When the daily cap is exhausted, `getAssetCurrentLimit()` still returns a non-zero value, yet every deposit attempt reverts.

### Finding Description

`getAssetCurrentLimit()` is the canonical public view function for querying how much of a given asset can still be deposited:

```solidity
// contracts/LRTDepositPool.sol L402-L409
function getAssetCurrentLimit(address asset) public view override returns (uint256) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
        return 0;
    }
    return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
}
```

It only subtracts cumulative deposits from the per-asset ceiling in `LRTConfig`. It does not consult `RSETH.maxMintAmountPerDay` or `RSETH.currentPeriodMintedAmount`.

The actual deposit path is:

```
depositETH() / depositAsset()
  └─ _beforeDeposit()          ← checks lrtConfig.depositLimitByAsset (same as getAssetCurrentLimit)
  └─ _mintRsETH()
       └─ IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint)
```

`RSETH.mint()` applies the `checkDailyMintLimit` modifier:

```solidity
// contracts/RSETH.sol L42-L56
modifier checkDailyMintLimit(uint256 amount) {
    if (block.timestamp >= periodStartTime + 1 days) {
        currentPeriodMintedAmount = 0;
        periodStartTime = getCurrentPeriodStartTime();
    }
    if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
        revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
    }
    currentPeriodMintedAmount += amount;
    _;
}
```

This is a second, independent gate that `getAssetCurrentLimit()` is entirely unaware of. The two limits are orthogonal: the per-asset cap is a cumulative lifetime ceiling; the daily mint cap resets every 24 hours and is enforced at the token level.

### Impact Explanation

Any user or off-chain integrator that calls `getAssetCurrentLimit()` to determine how much they can deposit will receive an inflated answer whenever the RSETH daily mint cap is exhausted. A subsequent deposit of that amount will revert with `DailyMintLimitExceeded`, even though the view function indicated capacity was available. This is a **Low** impact: the contract fails to deliver the promised return (a reliable deposit-capacity estimate), but no funds are lost because the transaction reverts cleanly.

### Likelihood Explanation

The daily mint cap is an active, manager-configured parameter (`setMaxMintAmountPerDay`). During periods of high deposit activity — exactly when integrators are most likely to query `getAssetCurrentLimit()` — the daily cap is most likely to be exhausted. The mismatch is therefore reachable under normal operating conditions by any unprivileged depositor.

### Recommendation

`getAssetCurrentLimit()` should also cap its return value by the remaining RSETH daily mint capacity, converted to asset units via the oracle. Concretely:

1. Read `RSETH.remainingDailyMintLimit()` (already implemented in `RSETH.sol` at line 265).
2. Convert the remaining rsETH mint headroom back to asset units using `LRTOracle.rsETHPrice()` and `LRTOracle.getAssetPrice(asset)`.
3. Return the minimum of the per-asset cap remainder and the converted daily mint headroom.

### Proof of Concept

1. `maxMintAmountPerDay` is set to 100 rsETH; `currentPeriodMintedAmount` is already 99 rsETH.
2. `getAssetCurrentLimit(ETH)` returns, say, 500 ETH (the per-asset cap has plenty of room).
3. A user calls `getAssetCurrentLimit(ETH)`, receives 500 ETH, and attempts to deposit 10 ETH (which would mint ~9.5 rsETH).
4. `_beforeDeposit` passes (10 ETH is within the per-asset cap).
5. `_mintRsETH` calls `RSETH.mint(user, 9.5e18)`.
6. `checkDailyMintLimit`: `99e18 + 9.5e18 = 108.5e18 > 100e18` → reverts with `DailyMintLimitExceeded`.
7. The user's transaction reverts despite `getAssetCurrentLimit()` having advertised 500 ETH of available capacity. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
