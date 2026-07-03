### Title
Block Stuffing Accumulates Multi-Day Yield Into Single Fee Mint, Triggering `DailyFeeMintLimitExceeded` and Freezing Price Updates — (`contracts/LRTOracle.sol`)

---

### Summary

An attacker can use block stuffing to prevent `updateRSETHPrice()` from being called for multiple days. When the price update is finally executed, the entire accumulated yield (from `swETH.getRate()` or any rebasing asset) is treated as a single-period TVL increase. The resulting protocol fee mint amount can exceed `maxFeeMintAmountPerDay`, causing `_checkAndUpdateDailyFeeMintLimit` to revert with `DailyFeeMintLimitExceeded`. Critically, this revert path is shared by both the public `updateRSETHPrice()` and the manager-only `updateRSETHPriceAsManager()`, so neither can succeed until the manager separately adjusts `maxFeeMintAmountPerDay`.

---

### Finding Description

`updateRSETHPrice()` is a permissionless `public` function. [1](#0-0) 

It delegates to `_updateRsETHPrice()`, which computes `totalETHInProtocol` by reading live oracle rates (including `SwETHPriceOracle.getAssetPrice` → `ISwETH.getRate()`). [2](#0-1) 

The TVL delta since the last update is treated as the reward for the current period:

```solidity
uint256 rewardAmount = totalETHInProtocol - previousTVL;
protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
``` [3](#0-2) 

The resulting fee is then checked against the daily cap:

```solidity
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(...);
}
``` [4](#0-3) 

There is no mechanism to amortize the fee across the N days during which the update was suppressed. If N days of yield are presented at once, the single-call fee is N× the expected daily fee.

`updateRSETHPriceAsManager()` provides no bypass — it calls the same `_updateRsETHPrice()` internal function and hits the same revert: [5](#0-4) [6](#0-5) 

The only recovery path is for the manager to first call `setMaxFeeMintAmountPerDay` to raise the cap, then retry the update — a two-step manual intervention.

---

### Impact Explanation

- `rsETHPrice` is not updated; all downstream consumers (deposit pool pricing, withdrawal valuations, pool exchange rates) read a stale price.
- Both the public and manager-gated price update entry points are simultaneously bricked.
- Recovery requires out-of-band manager action (`setMaxFeeMintAmountPerDay` + retry), introducing a window of stale pricing.

**Impact: Low — Block stuffing** (explicitly in scope).

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but economically rational if the attacker profits from stale pricing (e.g., holds a large short position on rsETH or exploits a downstream protocol that reads `rsETHPrice`). The attack requires no privileged access and is fully permissionless. The vulnerability is triggered by a small `maxFeeMintAmountPerDay` relative to the protocol's TVL and yield rate — a realistic configuration for a conservative daily cap.

---

### Recommendation

In `_checkAndUpdateDailyFeeMintLimit`, instead of reverting when the fee exceeds the daily cap, cap the minted fee at the remaining daily allowance and carry forward the uncollected fee, or skip fee minting for the excess. Alternatively, give `updateRSETHPriceAsManager()` its own internal path that bypasses the daily fee limit check (minting the full fee regardless of the cap), so the manager can always recover from a stuffed-block scenario without needing a separate `setMaxFeeMintAmountPerDay` call.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Unit test (Foundry) — no mainnet required
// 1. Deploy LRTOracle with a mock swETH oracle returning rate = 1e18
// 2. Set maxFeeMintAmountPerDay = 1e15 (tiny cap)
// 3. Simulate N=7 days passing: advance block.timestamp by 7 days
//    WITHOUT calling updateRSETHPrice (simulating block stuffing)
// 4. Advance mock swETH rate to 1e18 + 7 * dailyYield (7 days of accrued yield)
// 5. Call updateRSETHPrice()
// 6. Assert revert with DailyFeeMintLimitExceeded

function testBlockStuffingDailyFeeLimitDOS() public {
    // setup: small daily fee cap
    lrtOracle.setMaxFeeMintAmountPerDay(1e15);

    // simulate 7 days of block stuffing — no updateRSETHPrice called
    vm.warp(block.timestamp + 7 days);

    // swETH rate has accrued 7 days of ~4% APR yield
    mockSwETH.setRate(1e18 + 7 * 1.1e13); // ~7 days of daily yield

    // anyone calls updateRSETHPrice — reverts
    vm.expectRevert(ILRTOracle.DailyFeeMintLimitExceeded.selector);
    lrtOracle.updateRSETHPrice();

    // even manager is blocked
    vm.prank(manager);
    vm.expectRevert(ILRTOracle.DailyFeeMintLimitExceeded.selector);
    lrtOracle.updateRSETHPriceAsManager();
}
```

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L205-207)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }
```

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L303-303)
```text
            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
```

**File:** contracts/oracles/SwETHPriceOracle.sol (L34-40)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != swETHAddress) {
            revert InvalidAsset();
        }

        return ISwETH(swETHAddress).getRate();
    }
```
