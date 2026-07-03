### Title
`_checkAndUpdateDailyFeeMintLimit` revert permanently deadlocks `_updateRsETHPrice` when accumulated fee exceeds daily cap, freezing `rsETHPrice` and enabling yield theft - (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` unconditionally calls `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` before writing the new `rsETHPrice`. When accumulated staking rewards cause the single-update fee to exceed `maxFeeMintAmountPerDay`, this call reverts with `DailyFeeMintLimitExceeded`, leaving `rsETHPrice` permanently frozen at a stale (lower) value. The deadlock is self-reinforcing: the stale price understates `previousTVL`, which inflates the fee on every subsequent attempt. Both `updateRSETHPrice()` and `updateRSETHPriceAsManager()` are blocked. While `rsETHPrice` is frozen, new depositors receive excess rsETH (since `getRsETHAmountToMint = amount * assetPrice / rsETHPrice`), diluting existing holders and constituting theft of unclaimed yield.

---

### Finding Description

`_updateRsETHPrice()` computes the protocol fee in rsETH and then calls `_checkAndUpdateDailyFeeMintLimit` before updating `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol L299-L313
if (protocolFeeInETH > 0) {
    uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
    _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);  // <-- can revert
    ...
} else {
    _checkAndUpdateDailyFeeMintLimit(0);
}
rsETHPrice = newRsETHPrice;  // <-- never reached if above reverts
``` [1](#0-0) 

`_checkAndUpdateDailyFeeMintLimit` resets the daily counter if a day has passed, then reverts if the fee exceeds the cap:

```solidity
// contracts/LRTOracle.sol L197-L209
if (block.timestamp >= feePeriodStartTime + 1 days) {
    currentPeriodMintedFeeAmount = 0;
    feePeriodStartTime = getCurrentPeriodStartTime();
}
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(...);
}
``` [2](#0-1) 

**The deadlock mechanism:**

1. Protocol accumulates rewards over a period without price updates (e.g., infrequent calls, or a period where the oracle was paused and then unpaused).
2. `totalETHInProtocol > previousTVL` where `previousTVL = rsethSupply * rsETHPrice` uses the stale price.
3. `protocolFeeInETH = rewardAmount * protocolFeeInBPS / 10_000` is large.
4. `rsethAmountToMintAsProtocolFee = protocolFeeInETH / newRsETHPrice` exceeds `maxFeeMintAmountPerDay`.
5. `_checkAndUpdateDailyFeeMintLimit` reverts → `rsETHPrice` is never written.
6. Next day: the daily counter resets to 0, but `rsethAmountToMintAsProtocolFee` still exceeds `maxFeeMintAmountPerDay` (the single-update fee is larger than the cap itself).
7. **Self-reinforcing**: the frozen stale `rsETHPrice` understates `previousTVL`, making `rewardAmount` even larger on the next attempt, worsening the deadlock.

Both public entry points call `_updateRsETHPrice()` and are equally blocked:

```solidity
// contracts/LRTOracle.sol L87-L96
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
function updateRSETHPriceAsManager() external onlyLRTManager {
    _updateRsETHPrice();
}
``` [3](#0-2) 

**Concrete numerical example:**

```
TVL = 500,000 ETH
Protocol fee = 10% APY → ~0.027% per day → 135 ETH/day
rsETHPrice = 1.05 ETH → rsethAmountToMintAsProtocolFee ≈ 128.5 rsETH/day

If maxFeeMintAmountPerDay = 100 rsETH:
  → Every single call to updateRSETHPrice() reverts
  → rsETHPrice is permanently frozen
  → Deadlock is immediate and perpetual
```

**Consequence on deposits:**

`getRsETHAmountToMint` divides by the stale (lower) `rsETHPrice`:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [4](#0-3) 

A stale lower `rsETHPrice` causes new depositors to receive more rsETH than they are entitled to, directly diluting existing holders.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

While `rsETHPrice` is frozen at a stale lower value, every new deposit via `depositETH()` or `depositAsset()` mints excess rsETH to the depositor at the expense of existing rsETH holders. The yield that existing holders have already earned (reflected in the true higher TVL) is diluted away. Additionally, the protocol fee (unclaimed yield for the treasury) is permanently unclaimable until admin intervention. The deadlock is self-reinforcing and does not resolve on its own. [5](#0-4) 

---

### Likelihood Explanation

This occurs naturally under normal operating conditions whenever:

- `maxFeeMintAmountPerDay` is set to a value smaller than the fee generated in a single update interval (which is a function of TVL × fee rate × elapsed time), **or**
- The protocol experiences any gap in price updates (e.g., keeper downtime, gas spikes, or a brief pause-unpause cycle) that allows rewards to accumulate beyond the daily cap for a single call.

No attacker action is required. Any depositor, withdrawer, or public caller who triggers `updateRSETHPrice()` will observe the revert. The deadlock then persists indefinitely until an admin calls `setMaxFeeMintAmountPerDay` to raise the cap. [6](#0-5) 

---

### Recommendation

1. **Do not revert inside `_updateRsETHPrice` when the fee exceeds the daily cap.** Instead, cap the fee minted to `maxFeeMintAmountPerDay - currentPeriodMintedFeeAmount` and carry the remainder forward, or skip fee minting for that update while still writing the new `rsETHPrice`.
2. **Decouple fee minting from price updates.** The price write (`rsETHPrice = newRsETHPrice`) should never be gated on a secondary accounting check. Fee minting can be a separate, fallible step.
3. **Set `maxFeeMintAmountPerDay` relative to TVL and fee rate**, not as an absolute value, to avoid the cap being breached under normal growth.

---

### Proof of Concept

```
State:
  rsETHPrice = 1.00e18 (stale, last updated 2 days ago)
  rsethSupply = 500,000e18
  totalETHInProtocol = 502,700e18  (2 days of ~5% APY rewards)
  protocolFeeInBPS = 1000 (10%)
  maxFeeMintAmountPerDay = 100e18 rsETH

Step 1: Anyone calls updateRSETHPrice()
  previousTVL = 500,000e18 * 1.00e18 / 1e18 = 500,000e18
  rewardAmount = 502,700e18 - 500,000e18 = 2,700e18
  protocolFeeInETH = 2,700e18 * 1000 / 10,000 = 270e18
  newRsETHPrice = (502,700e18 - 270e18) / 500,000e18 ≈ 1.00486e18
  rsethAmountToMintAsProtocolFee = 270e18 / 1.00486e18 ≈ 268.7e18

Step 2: _checkAndUpdateDailyFeeMintLimit(268.7e18)
  currentPeriodMintedFeeAmount = 0 (new day)
  0 + 268.7e18 > 100e18 → revert DailyFeeMintLimitExceeded ✗

Step 3: rsETHPrice is NOT updated. Remains at 1.00e18.

Step 4: Next day, same call:
  previousTVL still uses stale rsETHPrice = 1.00e18
  rewardAmount is now even larger (3 days of rewards)
  rsethAmountToMintAsProtocolFee > 268.7e18 > 100e18 → revert again ✗

Step 5: New depositor calls depositETH(1 ETH):
  rsethAmountToMint = 1e18 * 1e18 / 1.00e18 = 1.000e18 rsETH
  (should be: 1e18 * 1e18 / 1.00486e18 ≈ 0.9952e18 rsETH)
  → Depositor receives ~0.0048 rsETH excess per ETH, at existing holders' expense.
``` [7](#0-6) [8](#0-7)

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

**File:** contracts/LRTOracle.sol (L130-135)
```text
    /// @dev set the maximum fee minting amount per day. Only onlyLRTManager is allowed
    /// @param _maxFeeMintAmountPerDay maximum amount of fee that can be minted per day
    function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
        maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
        emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
    }
```

**File:** contracts/LRTOracle.sol (L197-209)
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
```

**File:** contracts/LRTOracle.sol (L243-250)
```text
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L299-316)
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
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-669)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
