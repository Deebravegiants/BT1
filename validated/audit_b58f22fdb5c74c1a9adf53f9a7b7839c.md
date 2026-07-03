### Title
`checkDailyMintLimit` Modifier Renders `_mint` Unreachable When `maxMintAmountPerDay` Is Zero — (File: `contracts/RSETH.sol`)

---

### Summary

The `checkDailyMintLimit` modifier in `RSETH.sol` contains no guard for the case where `maxMintAmountPerDay == 0`. When this variable holds its default post-initialization value of zero, the limit check `currentPeriodMintedAmount + amount > maxMintAmountPerDay` collapses to `amount > 0`, which is always `true` for any meaningful mint. This makes the `_mint(to, amount)` call inside `RSETH.mint()` permanently unreachable — dead code — causing every rsETH mint to revert with `DailyMintLimitExceeded` until the manager explicitly sets a non-zero limit.

---

### Finding Description

After `RSETH.initialize()` is called, `maxMintAmountPerDay` is `0` (Solidity default). The `reinitialize()` function sets `periodStartTime` and `custodyAddress` but does **not** set `maxMintAmountPerDay`. The manager must separately call `setMaxMintAmountPerDay()`, and there is no validation preventing it from being set back to `0`.

The `checkDailyMintLimit` modifier:

```solidity
modifier checkDailyMintLimit(uint256 amount) {
    if (block.timestamp >= periodStartTime + 1 days) {
        currentPeriodMintedAmount = 0;
        periodStartTime = getCurrentPeriodStartTime();
    }

    // When maxMintAmountPerDay == 0, this is equivalent to: amount > 0
    if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
        revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
    }

    currentPeriodMintedAmount += amount;
    _;  // <-- _mint(to, amount) is NEVER reached when maxMintAmountPerDay == 0
}
``` [1](#0-0) 

When `maxMintAmountPerDay == 0`, the revert fires unconditionally for any `amount > 0`, making the `_mint(to, amount)` call in the function body dead code. [2](#0-1) 

The `remainingDailyMintLimit()` view function has a special-case guard `if (maxMintAmountPerDay == 0) return 0;`, confirming the developers treat `0` as a distinct meaningful state — but the modifier does not mirror this guard. [3](#0-2) 

The `setMaxMintAmountPerDay` setter accepts `0` without validation:

```solidity
function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
    maxMintAmountPerDay = _maxMintAmountPerDay;
    emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
}
``` [4](#0-3) 

---

### Impact Explanation

All rsETH minting flows through `RSETH.mint()` with the `checkDailyMintLimit` modifier. The primary user-facing entry points are `LRTDepositPool.depositETH()` and `LRTDepositPool.depositAsset()`, both of which call `_mintRsETH()` → `IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint)`. [5](#0-4) 

When `maxMintAmountPerDay == 0`, every call to `depositETH` and `depositAsset` reverts. Users cannot receive rsETH in exchange for their deposited ETH or LST assets. This constitutes a **temporary freezing of funds** — deposited assets are not at risk of theft, but the protocol's core deposit functionality is completely non-operational until the manager sets a non-zero limit.

**Impact rating: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

- `maxMintAmountPerDay` is `0` by default after `initialize()`.
- `reinitialize()` does not set it; a separate `setMaxMintAmountPerDay()` call is required.
- `setMaxMintAmountPerDay()` accepts `0` with no validation, so a manager can inadvertently re-enable the blocked state.
- The `LRTOracle.sol` fee-minting path (`_checkAndUpdateDailyFeeMintLimit`) has the identical pattern for `maxFeeMintAmountPerDay`, compounding the risk surface. [6](#0-5) 

**Likelihood: Medium.**

---

### Recommendation

Add a zero-value guard in `checkDailyMintLimit` to treat `maxMintAmountPerDay == 0` as "no limit" (consistent with the `remainingDailyMintLimit()` view function's intent), or add input validation in `setMaxMintAmountPerDay` to reject `0`. Apply the same fix to `_checkAndUpdateDailyFeeMintLimit` in `LRTOracle.sol`.

```solidity
modifier checkDailyMintLimit(uint256 amount) {
    if (maxMintAmountPerDay != 0) {
        if (block.timestamp >= periodStartTime + 1 days) {
            currentPeriodMintedAmount = 0;
            periodStartTime = getCurrentPeriodStartTime();
        }
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }
        currentPeriodMintedAmount += amount;
    }
    _;
}
```

---

### Proof of Concept

1. Deploy `RSETH` and call `initialize(admin, lrtConfig)`. `maxMintAmountPerDay` is `0`.
2. Call `reinitialize(periodStartTime, custodyAddress)`. `maxMintAmountPerDay` remains `0`.
3. As a user, call `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
4. Execution reaches `IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint)`.
5. Inside `checkDailyMintLimit`: `0 + rsethAmountToMint > 0` → `true` → reverts with `DailyMintLimitExceeded(rsethAmountToMint, 0)`.
6. The `_mint(to, amount)` call is never reached. All deposits revert until `setMaxMintAmountPerDay` is called with a non-zero value. [7](#0-6)

### Citations

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

**File:** contracts/RSETH.sol (L125-128)
```text
    function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
        maxMintAmountPerDay = _maxMintAmountPerDay;
        emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
    }
```

**File:** contracts/RSETH.sol (L229-240)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
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

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
    }
```
