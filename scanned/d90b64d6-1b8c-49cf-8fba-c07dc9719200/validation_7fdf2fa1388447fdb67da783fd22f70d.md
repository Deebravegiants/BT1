### Title
`getCurrentDay()` Arithmetic Underflow Causes View Functions to Revert Before `startTimestamp` — (`contracts/pools/RSETHPoolV2.sol`)

---

### Summary

In `RSETHPoolV2.sol` (and its variants), `getCurrentDay()` performs an unchecked subtraction `block.timestamp - startTimestamp`. When `startTimestamp` is set to a future value via `reinitialize()`, any call to `remainingDailyMintLimit()` or `getNextDailyLimitResetTimestamp()` before that timestamp is reached will revert with an arithmetic underflow, because Solidity 0.8.x uses checked arithmetic by default.

---

### Finding Description

`reinitialize()` (reinitializer version 3) explicitly requires `startTimestamp` to be in the future: [1](#0-0) 

This means there is always a window between deployment of the new configuration and the moment `startTimestamp` is reached. During this window, `getCurrentDay()` computes: [2](#0-1) 

Since `startTimestamp > block.timestamp`, the subtraction `block.timestamp - startTimestamp` underflows and reverts.

The `deposit()` function is correctly guarded by the `limitDailyMint` modifier, which checks `block.timestamp < startTimestamp` before calling `getCurrentDay()`: [3](#0-2) 

However, `remainingDailyMintLimit()` and `getNextDailyLimitResetTimestamp()` call `getCurrentDay()` directly with no such guard: [4](#0-3) 

The identical pattern exists across all pool variants:
- `contracts/pools/RSETHPoolV3.sol`
- `contracts/pools/RSETHPoolV2ExternalBridge.sol`
- `contracts/pools/RSETHPoolV3ExternalBridge.sol`
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`

---

### Impact Explanation

Any external caller (user, aggregator, UI, or on-chain integrator) invoking `remainingDailyMintLimit()` or `getNextDailyLimitResetTimestamp()` before `startTimestamp` is reached will receive a revert instead of the promised return value. The contract fails to deliver its stated view interface during the pre-start window. No funds are lost or frozen.

**Impact: Low** — Contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

`reinitialize()` enforces that `startTimestamp` must be in the future, so this window is guaranteed to exist every time the daily mint limit is configured. Any off-chain system, keeper, or integrating contract that queries these view functions during the pre-start window will encounter the revert. Likelihood is **medium** given the window is a normal operational state.

---

### Recommendation

Add the same pre-start guard used in `limitDailyMint` to `getCurrentDay()` itself, or add it to the two affected view functions:

```solidity
function getCurrentDay() public view returns (uint256) {
    if (block.timestamp < startTimestamp) return 0;
    return (block.timestamp - startTimestamp) / 1 days;
}
```

This mirrors the recommendation from the original M-01 report: check the pre-start condition before performing the subtraction.

---

### Proof of Concept

1. Admin calls `reinitialize(dailyMintLimit, block.timestamp + 7 days)` — sets `startTimestamp` to one week in the future.
2. Any caller immediately invokes `remainingDailyMintLimit()`.
3. Execution reaches `getCurrentDay()` → `block.timestamp - startTimestamp` → arithmetic underflow → revert.
4. Same revert occurs for `getNextDailyLimitResetTimestamp()`.
5. Both functions remain broken until `block.timestamp >= startTimestamp`. [2](#0-1) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L73-75)
```text
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }
```

**File:** contracts/pools/RSETHPoolV2.sol (L139-142)
```text
        // startTimestamp cannot be in the past
        if (block.timestamp > _startTimestamp) {
            revert InvalidStartTimestamp();
        }
```

**File:** contracts/pools/RSETHPoolV2.sol (L246-248)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L252-263)
```text
    function remainingDailyMintLimit() external view returns (uint256) {
        // If we're on a new day but no mint has occurred yet, treat dailyMintAmount as 0
        uint256 effectiveDailyMintAmount = (getCurrentDay() > lastMintDay) ? 0 : dailyMintAmount;

        return dailyMintLimit - effectiveDailyMintAmount;
    }

    /// @notice Gets the next daily mint limit reset timestamp
    /// @return uint256 The next daily mint limit reset timestamp
    function getNextDailyLimitResetTimestamp() external view returns (uint256) {
        return startTimestamp + (getCurrentDay() + 1) * 1 days;
    }
```
