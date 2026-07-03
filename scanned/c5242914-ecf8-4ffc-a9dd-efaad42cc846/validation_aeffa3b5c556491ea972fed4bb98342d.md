### Title
Block-Stuffing Allows Daily Fee Mint Cap Reset, Enabling Full `maxFeeMintAmountPerDay` Mint in a Single Call — (`contracts/LRTOracle.sol`)

---

### Summary

`updateRSETHPrice()` is an unrestricted public function. `_checkAndUpdateDailyFeeMintLimit` resets `currentPeriodMintedFeeAmount` to zero whenever `block.timestamp >= feePeriodStartTime + 1 days`. An attacker can block-stuff for the short window needed to push the clock past the period boundary, then allow the call to land in the new period with a fully reset counter, minting up to `maxFeeMintAmountPerDay` in a single call even though most of that capacity was already consumed in the prior period.

---

### Finding Description

`updateRSETHPrice()` carries no role guard: [1](#0-0) 

Inside `_checkAndUpdateDailyFeeMintLimit`, the period resets unconditionally when one day has elapsed: [2](#0-1) 

`getCurrentPeriodStartTime()` floors to the most recent period boundary, so a call that arrives even one second after `feePeriodStartTime + 1 days` resets both `currentPeriodMintedFeeAmount` and `feePeriodStartTime`: [3](#0-2) 

**Attack path:**

1. Observe that `currentPeriodMintedFeeAmount` is near `maxFeeMintAmountPerDay` (e.g., 95 % consumed) and the period boundary is ~1 hour away.
2. Block-stuff for that 1-hour window — fill every block with high-gas transactions so no one can land `updateRSETHPrice()`.
3. Once `block.timestamp >= feePeriodStartTime + 1 days`, stop stuffing and call `updateRSETHPrice()`.
4. `_checkAndUpdateDailyFeeMintLimit` resets `currentPeriodMintedFeeAmount = 0` and advances `feePeriodStartTime`.
5. The fee computed on the accumulated TVL increase (rewards from the stuffed window) is now checked against a fresh counter, so up to the full `maxFeeMintAmountPerDay` can be minted — far more than the ~5 % that remained in the old period.

The `pricePercentageLimit` guard does not block this: a 1-hour delay produces a negligible price increase (fractions of a basis point of staking yield), well below any realistic `pricePercentageLimit`. [4](#0-3) 

---

### Impact Explanation

The invariant "no more than `maxFeeMintAmountPerDay` rsETH may be minted as protocol fee within any rolling 24-hour window" is violated. The treasury receives up to `maxFeeMintAmountPerDay` of extra rsETH that should have been blocked by the remaining-capacity check, diluting all existing rsETH holders beyond the intended daily cap. This maps to **Low — Block stuffing** and **Low — Contract fails to deliver promised returns**.

---

### Likelihood Explanation

Block-stuffing on Ethereum mainnet is expensive but finite: the attacker only needs to stuff for the short remaining window before the period boundary (potentially minutes to an hour). The cost scales with the window size and current base fee. The attacker has no direct financial gain (fees go to the treasury), making this primarily a griefing/protocol-manipulation vector rather than a profit-driven exploit. Likelihood is **Low** but non-zero, especially on L2 deployments where block-stuffing is orders of magnitude cheaper.

---

### Recommendation

Decouple the period-reset logic from the call timestamp. Two concrete options:

1. **Carry-forward remaining capacity**: instead of resetting `currentPeriodMintedFeeAmount` to zero, compute how many full periods have elapsed and only reset if at least one full period has passed *since the last mint*, preserving the invariant across skipped periods.
2. **Cap fee to remaining capacity in the current period**: before resetting, mint only up to the remaining capacity of the expiring period, then start the new period with the remainder. This prevents a single call from consuming a full new-period budget for rewards that accrued across two periods.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// Foundry test (pseudo-code outline)

function test_blockStuffingBypassesDailyFeeCap() public {
    // Setup: feePeriodStartTime = T, maxFeeMintAmountPerDay = 100e18
    // Simulate 95 rsETH already minted this period
    vm.store(address(oracle), CURRENT_PERIOD_MINTED_SLOT, bytes32(uint256(95e18)));

    // Warp to 1 second past the period boundary (simulates block-stuffing success)
    vm.warp(feePeriodStartTime + 1 days + 1);

    // Simulate TVL increase large enough to generate 100e18 rsETH in fees
    // (mock getTotalEthInProtocol to return previousTVL + large reward)
    mockTVLIncrease(largeReward);

    uint256 treasuryBefore = rsETH.balanceOf(treasury);
    oracle.updateRSETHPrice();
    uint256 minted = rsETH.balanceOf(treasury) - treasuryBefore;

    // Without block-stuffing, only 5e18 (= 100e18 - 95e18) could have been minted
    // With block-stuffing past the boundary, up to 100e18 is minted
    assertEq(minted, 100e18); // full cap, not the 5e18 remainder
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

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```
