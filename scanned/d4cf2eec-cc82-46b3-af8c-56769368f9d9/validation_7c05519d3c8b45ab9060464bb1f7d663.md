### Title
Period-Reset Floor Arithmetic in `_checkAndUpdateDailyFeeMintLimit` Allows 2× Daily Fee Cap to Be Minted in 23 Hours — (`contracts/LRTOracle.sol`)

---

### Summary

When no `updateRSETHPrice()` call occurs for more than one full day, the floor-based period-reset in `_checkAndUpdateDailyFeeMintLimit` sets `feePeriodStartTime` to the *floor* of the current day boundary rather than `block.timestamp`. This creates a shortened next period that expires sooner than 24 hours after the first reset, allowing a second full `maxFeeMintAmountPerDay` mint to occur only 23 hours later — yielding 2 × `maxFeeMintAmountPerDay` in a 23-hour window and violating the intended daily dilution cap.

---

### Finding Description

`updateRSETHPrice()` is unrestricted (`public`, no role check): [1](#0-0) 

Inside `_updateRsETHPrice()`, every execution path calls `_checkAndUpdateDailyFeeMintLimit`: [2](#0-1) 

`_checkAndUpdateDailyFeeMintLimit` resets the period using `getCurrentPeriodStartTime()`, which floors to the nearest completed day boundary: [3](#0-2) 

`getCurrentPeriodStartTime()` performs integer-division flooring: [4](#0-3) 

**Concrete timeline** (let T0 = `feePeriodStartTime`):

| Time | Action | `feePeriodStartTime` after | `currentPeriodMintedFeeAmount` |
|------|--------|---------------------------|-------------------------------|
| T0 | Period initialized | T0 | 0 |
| T0 + 25h | First `updateRSETHPrice()` call | T0 + 24h (floored) | `maxFeeMintAmountPerDay` |
| T0 + 48h | Second call (only 23h later) | T0 + 48h | `maxFeeMintAmountPerDay` |

At T0 + 25h, `daysElapsed = (T0+25h − T0) / 24h = 1`, so `feePeriodStartTime` is set to `T0 + 24h` — one hour in the past. The new period therefore expires at `T0 + 48h`, only **23 hours** after the first reset. A second full `maxFeeMintAmountPerDay` is available immediately at T0 + 48h.

The fee minting itself requires `totalETHInProtocol > previousTVL` (actual staking rewards): [5](#0-4) 

Over a 25-hour gap without updates, staking rewards accumulate naturally, satisfying this condition without any manipulation.

---

### Impact Explanation

rsETH holders are diluted by protocol fee minting. The `maxFeeMintAmountPerDay` cap is the sole on-chain protection against excessive dilution. This bug allows that cap to be consumed twice in 23 hours instead of 48 hours — a 2× acceleration of yield extraction from rsETH holders to the treasury. The impact is **High: Theft of unclaimed yield**.

---

### Likelihood Explanation

The precondition — no `updateRSETHPrice()` call for more than 24 hours — is realistic: keeper/bot failures, network congestion, or deliberate withholding of updates can all produce this gap. Once the gap exists, the exploit requires only two public function calls with no special privileges. Any EOA can execute it.

---

### Recommendation

Replace the floor-based reset with a forward-anchored reset that sets `feePeriodStartTime = block.timestamp` (or `feePeriodStartTime + 1 days` to preserve alignment), ensuring the next period always runs a full 24 hours from the moment of reset:

```solidity
function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
    if (block.timestamp >= feePeriodStartTime + 1 days) {
        currentPeriodMintedFeeAmount = 0;
-       feePeriodStartTime = getCurrentPeriodStartTime();
+       feePeriodStartTime = block.timestamp; // or feePeriodStartTime + 1 days for strict alignment
    }
    ...
}
```

Alternatively, if calendar-day alignment is required, enforce that the gap between two consecutive mints can never be less than 24 hours by tracking `lastMintTimestamp` and reverting if `block.timestamp < lastMintTimestamp + 1 days`.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Foundry test (forge test --match-test testDoubleFeeMintIn23Hours)
contract DoubleFeeMintTest is Test {
    LRTOracle oracle;
    // ... setup: deploy oracle, set feePeriodStartTime = block.timestamp,
    //            set maxFeeMintAmountPerDay = 100e18,
    //            ensure TVL increases by enough to hit the cap

    function testDoubleFeeMintIn23Hours() public {
        uint256 T0 = oracle.feePeriodStartTime();

        // Simulate 25 hours passing with no update (staking rewards accrue)
        vm.warp(T0 + 25 hours);
        oracle.updateRSETHPrice(); // First call: resets period to T0+24h, mints maxFeeMintAmountPerDay

        assertEq(oracle.feePeriodStartTime(), T0 + 24 hours);
        assertEq(oracle.currentPeriodMintedFeeAmount(), 100e18); // full cap used

        // Only 23 more hours pass — total elapsed from T0 is 48h
        vm.warp(T0 + 48 hours);
        oracle.updateRSETHPrice(); // Second call: resets period to T0+48h, mints another maxFeeMintAmountPerDay

        // 2 * maxFeeMintAmountPerDay minted in 23 hours (T0+25h → T0+48h)
        // Invariant violated: daily cap bypassed
    }
}
```

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

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L303-310)
```text
            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
```
