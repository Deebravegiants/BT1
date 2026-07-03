### Title
`getCurrentDay()` Reverts Before `startTimestamp`, Causing `remainingDailyMintLimit()` and `getNextDailyLimitResetTimestamp()` to Revert - (File: contracts/pools/RSETHPoolV2.sol, contracts/pools/RSETHPoolV3.sol)

---

### Summary

`getCurrentDay()` performs an unchecked `block.timestamp - startTimestamp` subtraction. Because `reinitialize` enforces that `startTimestamp` must be in the future, there is always a window during which calling `getCurrentDay()` triggers an arithmetic underflow revert (Solidity 0.8.x checked arithmetic). The public view functions `remainingDailyMintLimit()` and `getNextDailyLimitResetTimestamp()` both delegate to `getCurrentDay()` without any pre-condition guard, so they revert during this window. The state-changing `deposit()` path is separately protected by an explicit guard in the `limitDailyMint` modifier, but the view functions are not.

---

### Finding Description

`RSETHPoolV2` and `RSETHPoolV3` both expose a `getCurrentDay()` public view function:

```solidity
function getCurrentDay() public view returns (uint256) {
    return (block.timestamp - startTimestamp) / 1 days;
}
``` [1](#0-0) [2](#0-1) 

`startTimestamp` is set by `reinitialize`, which enforces it must be **at or after** the current block:

```solidity
if (block.timestamp > _startTimestamp) {
    revert InvalidStartTimestamp();
}
``` [3](#0-2) [4](#0-3) 

This guarantees a window — from the moment `reinitialize` is called until `block.timestamp` reaches `startTimestamp` — during which `block.timestamp < startTimestamp`. In Solidity 0.8.27, the subtraction `block.timestamp - startTimestamp` reverts with an arithmetic panic.

Both `remainingDailyMintLimit()` and `getNextDailyLimitResetTimestamp()` call `getCurrentDay()` unconditionally:

```solidity
function remainingDailyMintLimit() external view returns (uint256) {
    uint256 effectiveDailyMintAmount = (getCurrentDay() > lastMintDay) ? 0 : dailyMintAmount;
    return dailyMintLimit - effectiveDailyMintAmount;
}

function getNextDailyLimitResetTimestamp() external view returns (uint256) {
    return startTimestamp + (getCurrentDay() + 1) * 1 days;
}
``` [5](#0-4) [6](#0-5) 

By contrast, the `limitDailyMint` modifier — the only internal caller of `getCurrentDay()` — is correctly guarded:

```solidity
if (block.timestamp < startTimestamp) {
    revert MintBeforeStartTimestamp();
}
``` [7](#0-6) [8](#0-7) 

The view functions have no equivalent guard, so they revert during the pre-`startTimestamp` window.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

`remainingDailyMintLimit()` and `getNextDailyLimitResetTimestamp()` are public view functions intended to be queried by off-chain clients, integrators, and front-ends to understand the current minting capacity and when the limit resets. During the pre-`startTimestamp` window, both functions revert unconditionally, returning no usable data. No funds are at risk and no state-changing path is broken (the `deposit()` path is separately guarded), but the contract fails to deliver its promised informational interface.

---

### Likelihood Explanation

**Medium.** Every deployment that calls `reinitialize` with a future `startTimestamp` (which is the only valid input) creates this window. The window length equals `startTimestamp - block.timestamp` at the time of `reinitialize`, which can be hours or days. Any off-chain client, aggregator, or integration that queries `remainingDailyMintLimit()` or `getNextDailyLimitResetTimestamp()` during this window will receive a revert. No special attacker action is required — any public caller triggers it.

---

### Recommendation

Add a pre-condition guard in `getCurrentDay()` (or in each calling view function) that returns a safe sentinel value when `block.timestamp < startTimestamp`, mirroring the guard already present in `limitDailyMint`:

```solidity
function getCurrentDay() public view returns (uint256) {
    if (block.timestamp < startTimestamp) return 0;
    return (block.timestamp - startTimestamp) / 1 days;
}
```

Alternatively, `remainingDailyMintLimit()` can explicitly return `dailyMintLimit` (full limit available, no minting has occurred yet) when `block.timestamp < startTimestamp`, and `getNextDailyLimitResetTimestamp()` can return `startTimestamp` directly in that case.

---

### Proof of Concept

1. Admin calls `reinitialize(dailyMintLimit, block.timestamp + 1 days)` on `RSETHPoolV2` or `RSETHPoolV3`.
2. `startTimestamp` is now set to `block.timestamp + 1 days`.
3. Any external caller immediately calls `remainingDailyMintLimit()`.
4. Internally, `getCurrentDay()` computes `block.timestamp - startTimestamp`, which is `block.timestamp - (block.timestamp + 1 days)` — a negative value — triggering an arithmetic underflow revert in Solidity 0.8.27.
5. `remainingDailyMintLimit()` reverts with a panic instead of returning the expected `dailyMintLimit`.
6. Same revert occurs for `getNextDailyLimitResetTimestamp()`.
7. The same pattern is present in `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`, which share the same `getCurrentDay()` implementation. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L73-75)
```text
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
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

**File:** contracts/pools/RSETHPoolV3.sol (L97-99)
```text
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }
```

**File:** contracts/pools/RSETHPoolV3.sol (L179-198)
```text
    function reinitialize(
        uint256 _dailyMintLimit,
        uint256 _startTimestamp
    )
        external
        reinitializer(2)
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

**File:** contracts/pools/RSETHPoolV3.sol (L339-341)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L345-356)
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
