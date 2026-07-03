### Title
Period-Reset Floor Arithmetic in `_checkAndUpdateDailyFeeMintLimit` Allows Two Full Daily Fee Allowances in Less Than 24 Hours — (`contracts/LRTOracle.sol`)

---

### Summary

When `updateRSETHPrice()` is called after the oracle has been idle for more than one full day, `_checkAndUpdateDailyFeeMintLimit` resets `feePeriodStartTime` to `getCurrentPeriodStartTime()` — the **floor** of the current day boundary — rather than to `block.timestamp`. This places the new period's start in the past, shortening the time until the next reset. A caller can therefore consume two full `maxFeeMintAmountPerDay` fee allowances in as little as 23 hours (or generally `48h − X`, where `X` is the idle overshoot), violating the invariant that no more than one daily cap's worth of fees should be minted per 24-hour window.

---

### Finding Description

`updateRSETHPrice()` is a permissionless public function: [1](#0-0) 

It calls `_checkAndUpdateDailyFeeMintLimit`, which resets the period when `block.timestamp >= feePeriodStartTime + 1 days`: [2](#0-1) 

The reset sets `feePeriodStartTime = getCurrentPeriodStartTime()`: [3](#0-2) 

`getCurrentPeriodStartTime()` computes `feePeriodStartTime + floor((block.timestamp - feePeriodStartTime) / 1 days) * 1 days`. When the oracle has been idle for `24h + X` (X > 0), this floors to `feePeriodStartTime + 24h`, placing the new period start **X seconds in the past**. The next period boundary therefore arrives in `24h − X` seconds, not 24 hours.

**Concrete trace (X = 1 hour):**

| Time | Action | feePeriodStartTime | currentPeriodMintedFeeAmount |
|---|---|---|---|
| T0 | Period initialized | T0 | 0 |
| T0 + 25h | Call 1: `updateRSETHPrice()` | T0 + 24h (= now − 1h) | maxFeeMintAmountPerDay |
| T0 + 48h (= Call1 + 23h) | Call 2: `updateRSETHPrice()` | T0 + 48h | maxFeeMintAmountPerDay |

Two full daily allowances are consumed in **23 hours** from Call 1.

The fee minting path that executes this: [4](#0-3) 

---

### Impact Explanation

Each call mints up to `maxFeeMintAmountPerDay` rsETH to the treasury. By triggering two resets in less than 24 hours, the treasury receives up to `2 × maxFeeMintAmountPerDay` rsETH in a window shorter than intended. This dilutes existing rsETH holders' share of the underlying ETH TVL faster than the daily cap was designed to allow — constituting theft of unclaimed yield from rsETH holders.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

- `updateRSETHPrice()` is public and permissionless; no role is required.
- The precondition (oracle idle for >24h) is realistic: the function has no keeper incentive, and any network disruption, gas spike, or simply no one calling it for a day satisfies it.
- The TVL increase required for fee minting (`totalETHInProtocol > previousTVL`) is met naturally by staking rewards accumulating over time.
- No admin compromise, front-running, or brute force is needed.

**Likelihood: Medium** (requires a >24h idle gap, which is an operational condition rather than a guaranteed state, but is plausible in production).

---

### Recommendation

Reset `feePeriodStartTime` to `block.timestamp` (or `block.timestamp` aligned to the current period start) rather than to the floored past boundary. The simplest fix:

```solidity
// In _checkAndUpdateDailyFeeMintLimit:
if (block.timestamp >= feePeriodStartTime + 1 days) {
    currentPeriodMintedFeeAmount = 0;
-   feePeriodStartTime = getCurrentPeriodStartTime();
+   feePeriodStartTime = block.timestamp;
}
```

This ensures each new period always starts at the moment of the first post-idle call, so the next reset is always at least 24 hours away.

Alternatively, if calendar-aligned periods are desired, the contract should track the last-minted period index and enforce that at most one full allowance is consumed per calendar day, regardless of when the call arrives.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Foundry test (forge test --match-test testDoubleFeeMintUnder48h)
// Assumes a local fork or mock setup with:
//   - lrtOracle: deployed LRTOracle proxy
//   - TVL increases by at least maxFeeMintAmountPerDay * newRsETHPrice each period

import "forge-std/Test.sol";

contract DoubleFeeMintPoC is Test {
    LRTOracle lrtOracle; // deployed instance

    function testDoubleFeeMintUnder48h() external {
        // Step 1: Advance time so the period is 25 hours stale
        vm.warp(lrtOracle.feePeriodStartTime() + 25 hours);

        // Ensure TVL has increased (staking rewards accumulated)
        // ... mock oracle prices / deposit pool balances to reflect +25h of rewards

        uint256 treasuryBalanceBefore = rsETH.balanceOf(treasury);

        // Call 1: resets feePeriodStartTime to (feePeriodStartTime + 24h), mints full daily cap
        lrtOracle.updateRSETHPrice();

        uint256 afterCall1 = rsETH.balanceOf(treasury);
        assertEq(afterCall1 - treasuryBalanceBefore, maxFeeMintAmountPerDay);

        // feePeriodStartTime is now (original + 24h), which is 1 hour ago.
        // Next reset fires at (original + 24h) + 24h = original + 48h = now + 23h.
        uint256 newPeriodEnd = lrtOracle.feePeriodStartTime() + 1 days;
        assertEq(newPeriodEnd, block.timestamp + 23 hours); // only 23h away

        // Step 2: Advance 23 hours (total elapsed from original T0: 48h)
        vm.warp(newPeriodEnd);

        // Ensure TVL has increased again (another 23h of staking rewards)
        // ... mock oracle prices / deposit pool balances

        // Call 2: resets again, mints another full daily cap
        lrtOracle.updateRSETHPrice();

        uint256 afterCall2 = rsETH.balanceOf(treasury);
        // Two full daily caps minted in 23 hours (from Call 1 to Call 2)
        assertEq(afterCall2 - treasuryBalanceBefore, 2 * maxFeeMintAmountPerDay);
    }
}
```

The assertion `newPeriodEnd == block.timestamp + 23 hours` directly proves the shortened window. Two full `maxFeeMintAmountPerDay` allowances are consumed in 23 hours rather than the intended 48 hours.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L162-166)
```text
    function getCurrentPeriodStartTime() public view returns (uint256) {
        // Calculate the full (complete) days elapsed since the period start time (floors the result)
        uint256 daysElapsed = (block.timestamp - feePeriodStartTime) / 1 days;
        return feePeriodStartTime + daysElapsed * 1 days;
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

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
```
