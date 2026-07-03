### Title
`_updateRsETHPrice` passes unbounded fee amount to `_checkAndUpdateDailyFeeMintLimit`, causing oracle update DoS when rewards exceed daily cap — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` computes `rsethAmountToMintAsProtocolFee` from live protocol rewards and passes it directly to `_checkAndUpdateDailyFeeMintLimit()`, which performs a hard revert when the fee amount exceeds `maxFeeMintAmountPerDay`. Because both the public `updateRSETHPrice()` and the manager-only `updateRSETHPriceAsManager()` route through `_updateRsETHPrice()`, neither path can bypass this revert. When protocol rewards in a single period legitimately exceed the configured daily cap, every oracle update attempt reverts, freezing the rsETH price.

---

### Finding Description

In `_updateRsETHPrice()`, the fee to mint is computed as:

```solidity
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);   // line 303
``` [1](#0-0) 

Inside `_checkAndUpdateDailyFeeMintLimit`, the check is unconditional:

```solidity
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
}
``` [2](#0-1) 

Because `currentPeriodMintedFeeAmount` is reset to `0` at the start of each new period, the effective check each day is simply `rsethAmountToMintAsProtocolFee > maxFeeMintAmountPerDay`. There is no fallback path: the function does not cap the fee, skip minting, or emit a partial-fee event — it reverts entirely, rolling back the price update.

Both entry points call the same internal function:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
function updateRSETHPriceAsManager() external onlyLRTManager {
    _updateRsETHPrice();
}
``` [3](#0-2) 

So no caller — public or privileged — can update the price while the condition holds. The only administrative escape is to call `setMaxFeeMintAmountPerDay()` to raise the cap, but this requires the team to notice the failure and act.

---

### Impact Explanation

**Temporary (or sustained) freezing of the rsETH oracle price.** While the price is frozen:

1. `LRTDepositPool.getRsETHAmountToMint()` uses the stale stored `rsETHPrice`, so depositors receive rsETH at an outdated (lower) rate, diluting existing holders.
2. `LRTWithdrawalManager.unlockQueue()` reads `lrtOracle.rsETHPrice()` to compute payout amounts; a stale price causes incorrect rsETH-to-asset conversions for queued withdrawers.
3. If rewards consistently exceed `maxFeeMintAmountPerDay` (e.g., after a large TVL increase), the freeze is effectively permanent until governance intervenes.

This matches **Medium — Temporary freezing of funds** (withdrawal queue desync / oracle staleness). [4](#0-3) 

---

### Likelihood Explanation

`rsethAmountToMintAsProtocolFee` is derived from `(totalETHInProtocol - previousTVL) * protocolFeeInBPS / 10_000 / newRsETHPrice`. For a protocol with hundreds of thousands of ETH in TVL, a single day's staking rewards (≈ 3–4 % APR / 365 ≈ 0.008–0.011 % per day) can produce a fee amount that exceeds a conservatively set `maxFeeMintAmountPerDay`. The condition is reachable in normal operation without any attacker involvement; it requires no special permissions and no price manipulation.

---

### Recommendation

Replace the hard revert with a graceful cap. If the computed fee exceeds the remaining daily allowance, mint only up to the limit and discard the excess (or carry it forward):

```diff
- _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
- if (rsethAmountToMintAsProtocolFee > 0) {
+ uint256 remainingLimit = maxFeeMintAmountPerDay > currentPeriodMintedFeeAmount
+     ? maxFeeMintAmountPerDay - currentPeriodMintedFeeAmount : 0;
+ rsethAmountToMintAsProtocolFee = rsethAmountToMintAsProtocolFee > remainingLimit
+     ? remainingLimit : rsethAmountToMintAsProtocolFee;
+ _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
+ if (rsethAmountToMintAsProtocolFee > 0) {
```

This mirrors the Ajna fix: instead of reverting when the value exceeds the bound, clamp it to the boundary and continue.

---

### Proof of Concept

1. Protocol has 100 000 ETH TVL; `protocolFeeInBPS = 1000` (10 %); daily rewards ≈ 8 ETH; fee ≈ 0.8 ETH worth of rsETH.
2. Admin sets `maxFeeMintAmountPerDay = 0.5 ETH` worth of rsETH (conservative cap).
3. Anyone calls `updateRSETHPrice()`.
4. `_updateRsETHPrice()` computes `rsethAmountToMintAsProtocolFee ≈ 0.8e18 / rsETHPrice`.
5. `_checkAndUpdateDailyFeeMintLimit(0.8e18/price)` evaluates `0 + 0.8e18/price > 0.5e18/price` → `true` → `revert DailyFeeMintLimitExceeded`.
6. `updateRSETHPrice()` reverts. `updateRSETHPriceAsManager()` also reverts (same code path).
7. `rsETHPrice` remains at yesterday's value. Depositors mint rsETH at the stale rate; withdrawal queue unlocking uses the stale rate.
8. Condition persists every day until `setMaxFeeMintAmountPerDay` is called. [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
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

**File:** contracts/LRTOracle.sol (L214-316)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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
        }

        // downside protection — pause if price drops too far
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
    }
```
