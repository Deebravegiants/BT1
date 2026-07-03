### Title
Daily Minting Limit Can Be Bypassed at Day Boundary — (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV2.sol`, `contracts/pools/RSETHPoolV2ExternalBridge.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

The `limitDailyMint` modifier across all L2 pool contracts uses `getCurrentDay()`, which computes `(block.timestamp - startTimestamp) / 1 days` via integer division. Because the day counter increments discretely at exact multiples of 86400 seconds from `startTimestamp`, an unprivileged depositor can mint up to the full `dailyMintLimit` at the last block of day N and immediately mint another full `dailyMintLimit` at the first block of day N+1 — effectively doubling the daily minting cap in just two consecutive blocks.

---

### Finding Description

`getCurrentDay()` is defined identically in all affected pool contracts:

```solidity
function getCurrentDay() public view returns (uint256) {
    return (block.timestamp - startTimestamp) / 1 days;
}
```

The `limitDailyMint` modifier resets `dailyMintAmount` whenever `currentDay > lastMintDay`:

```solidity
uint256 currentDay = getCurrentDay();

if (currentDay > lastMintDay) {
    lastMintDay = currentDay;
    dailyMintAmount = 0;
}

if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
    revert DailyMintLimitExceeded();
}

dailyMintAmount += rsETHAmount;
```

Because `getCurrentDay()` uses integer division, the day boundary is a hard edge: at `startTimestamp + N * 86400 - 1` the result is `N-1`, and at `startTimestamp + N * 86400` it becomes `N`. There is no overlap or grace period. An attacker can:

1. **Block A** (`block.timestamp = startTimestamp + N * 86400 - 1`): `getCurrentDay()` returns `N-1`. `lastMintDay` is already `N-1`, so no reset. Attacker deposits enough to mint exactly `dailyMintLimit` rsETH. `dailyMintAmount = dailyMintLimit`.
2. **Block B** (`block.timestamp = startTimestamp + N * 86400`): `getCurrentDay()` returns `N > lastMintDay`. `dailyMintAmount` resets to `0`. Attacker deposits again and mints another `dailyMintLimit` rsETH.

Total minted: **2 × `dailyMintLimit`** in two consecutive blocks (seconds apart on L2 chains with fast block times).

This is present in all five pool variants:
- `RSETHPoolV3.limitDailyMint` — lines 96–125
- `RSETHPoolV2.limitDailyMint` — lines 72–94
- `RSETHPoolV2ExternalBridge.limitDailyMint` — lines 104–126
- `RSETHPoolV3ExternalBridge.limitDailyMint` — lines 130–158
- `RSETHPoolV3WithNativeChainBridge.limitDailyMint` — lines 108–136

---

### Impact Explanation

The daily minting limit is the primary circuit breaker protecting against excessive rsETH issuance on L2 (e.g., in response to a stale or manipulated oracle rate). Bypassing it allows an attacker to mint 2× the intended daily cap in two blocks. On L2 chains (Arbitrum, Optimism, Base, Linea) where block times are 1–2 seconds, both transactions can be submitted in the same bundle or within seconds of each other. This undermines the security control entirely, enabling excessive wrsETH issuance relative to the underlying ETH deposited, which can lead to **temporary freezing of funds** (pool insolvency / inability to honor redemptions) or **protocol insolvency** if the oracle rate is simultaneously stale.

**Impact: Medium — Temporary freezing of funds / bypass of the daily minting circuit breaker.**

---

### Likelihood Explanation

No special privileges are required. Any depositor can monitor `startTimestamp` and `lastMintDay` on-chain, compute the exact day boundary, and submit two back-to-back deposit transactions. On L2 chains with 1–2 second block times, this is trivially executable. The attacker only needs to hold enough ETH (or supported LST) to fill the daily limit twice.

**Likelihood: High.**

---

### Recommendation

Replace the discrete day-counter comparison with a continuous timestamp-based window. Track the start of the current period as a stored timestamp and reset when `block.timestamp >= periodStart + 1 days`:

```solidity
uint256 public mintPeriodStart;

modifier limitDailyMint(uint256 amount, address token) {
    if (block.timestamp < startTimestamp) revert MintBeforeStartTimestamp();

    // Reset if a full 24-hour window has elapsed
    if (block.timestamp >= mintPeriodStart + 1 days) {
        mintPeriodStart = block.timestamp;
        dailyMintAmount = 0;
    }

    uint256 rsETHAmount = /* compute as before */;

    if (dailyMintAmount + rsETHAmount > dailyMintLimit) revert DailyMintLimitExceeded();
    dailyMintAmount += rsETHAmount;
    _;
}
```

This ensures the 24-hour window is always measured from the last reset, eliminating the exploitable hard boundary.

---

### Proof of Concept

Assume `startTimestamp = 1_000_000`, `dailyMintLimit = 100 ether`.

| Step | `block.timestamp` | `getCurrentDay()` | `lastMintDay` | `dailyMintAmount` before | Action | `dailyMintAmount` after |
|------|-------------------|-------------------|---------------|--------------------------|--------|-------------------------|
| 1 | 1,086,399 | 0 | 0 | 0 | Mint 100 ETH → 100 wrsETH | 100 ether |
| 2 | 1,086,400 | **1** | 0 → **1** | **reset to 0** | Mint 100 ETH → 100 wrsETH | 100 ether |

**Result:** 200 wrsETH minted (2× `dailyMintLimit`) in two consecutive blocks, bypassing the intended daily cap. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L339-341)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L72-94)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L104-126)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L130-158)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L108-136)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
```
