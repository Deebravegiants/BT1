The vulnerability is real. Let me trace through the exact code.

**`reinitialize(uint256, uint256)` (reinitializer(3))** sets `dailyMintLimit` and `startTimestamp` but does **not** reset `lastMintDay` or `dailyMintAmount`: [1](#0-0) 

After the new `startTimestamp` passes, `getCurrentDay()` returns `0`: [2](#0-1) 

The reset condition in `limitDailyMint` is `currentDay > lastMintDay`: [3](#0-2) 

With `currentDay = 0` and `lastMintDay = 50`, `0 > 50` is false — `dailyMintAmount` is never reset. The stale `dailyMintAmount` from the previous epoch persists and blocks minting until `getCurrentDay()` exceeds `lastMintDay` (i.e., day 51 of the new epoch). `remainingDailyMintLimit()` has the same flaw: [4](#0-3) 

---

### Title
State desync between `lastMintDay` and new `startTimestamp` after `reinitialize(3)` blocks deposits for up to N days — (`contracts/pools/RSETHPoolV2.sol`)

### Summary
`reinitialize(uint256,uint256)` resets `startTimestamp` to a new epoch but does not reset `lastMintDay` or `dailyMintAmount`. After the new epoch begins, `getCurrentDay()` returns `0`, but `lastMintDay` retains its old value (e.g., `50`). The reset guard `currentDay > lastMintDay` evaluates to `0 > 50 = false`, so `dailyMintAmount` is never cleared and the accumulated mint amount from the previous epoch blocks all new deposits until day `lastMintDay + 1` of the new epoch.

### Finding Description
In `limitDailyMint`, the daily counter resets only when `getCurrentDay() > lastMintDay`. `getCurrentDay()` is computed as `(block.timestamp - startTimestamp) / 1 days`, so it resets to `0` whenever `startTimestamp` is updated. If `lastMintDay` was `50` before `reinitialize(3)`, the condition `0 > 50` is permanently false for the first 51 days of the new epoch. The stale `dailyMintAmount` (e.g., `99e18`) remains, and any deposit that would push `dailyMintAmount + rsETHAmount > dailyMintLimit` reverts with `DailyMintLimitExceeded`. The fix — resetting `lastMintDay = 0` and `dailyMintAmount = 0` inside `reinitialize(uint256,uint256)` — is absent.

### Impact Explanation
**Medium — Temporary freezing of funds.** Deposits are blocked (or severely throttled to the residual `dailyMintLimit - dailyMintAmount` headroom) for up to `lastMintDay` days after the new epoch starts. With `lastMintDay = 50`, the pool is effectively frozen for 51 days. No funds are permanently lost, but user deposits are rejected during this window.

### Likelihood Explanation
Moderate. `reinitialize(3)` is a one-shot upgrade function callable by `DEFAULT_ADMIN_ROLE`. Any legitimate contract upgrade that resets the epoch (e.g., migrating to a new schedule) will trigger this bug automatically. No attacker action is required; the admin's own correct use of the function causes the desync.

### Recommendation
In `reinitialize(uint256,uint256)`, explicitly reset the daily mint state alongside the new `startTimestamp`:

```solidity
dailyMintLimit = _dailyMintLimit;
startTimestamp = _startTimestamp;
lastMintDay = 0;       // reset epoch counter
dailyMintAmount = 0;   // clear accumulated amount
```

### Proof of Concept
```solidity
// 1. Pool active: lastMintDay = 50, dailyMintAmount = 99e18, dailyMintLimit = 100e18
// 2. Admin calls reinitialize(100e18, block.timestamp + 1 days)
//    → sets startTimestamp = T+1day, does NOT reset lastMintDay/dailyMintAmount
// 3. At T+1day+1sec: getCurrentDay() = 0
// 4. limitDailyMint: currentDay(0) > lastMintDay(50) → false → no reset
// 5. dailyMintAmount + any_deposit > 100e18 → DailyMintLimitExceeded for all but 1e18
// 6. assert remainingDailyMintLimit() == dailyMintLimit  ← FAILS (returns 1e18, not 100e18)
// 7. Deposits blocked until getCurrentDay() = 51 (day 51 of new epoch)
```

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L82-85)
```text
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }
```

**File:** contracts/pools/RSETHPoolV2.sol (L127-146)
```text
    function reinitialize(
        uint256 _dailyMintLimit,
        uint256 _startTimestamp
    )
        external
        reinitializer(3)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }

        // startTimestamp cannot be in the past
        if (block.timestamp > _startTimestamp) {
            revert InvalidStartTimestamp();
        }

        dailyMintLimit = _dailyMintLimit;
        startTimestamp = _startTimestamp;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L246-248)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L252-257)
```text
    function remainingDailyMintLimit() external view returns (uint256) {
        // If we're on a new day but no mint has occurred yet, treat dailyMintAmount as 0
        uint256 effectiveDailyMintAmount = (getCurrentDay() > lastMintDay) ? 0 : dailyMintAmount;

        return dailyMintLimit - effectiveDailyMintAmount;
    }
```
