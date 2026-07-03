### Title
Stale `rsETHPrice` After Early Return in `_updateRsETHPrice()` Enables Over-Commitment and Over-Payout on Withdrawal - (File: contracts/LRTOracle.sol)

---

### Summary

In `LRTOracle._updateRsETHPrice()`, when a price drop exceeds `pricePercentageLimit`, the function pauses the protocol and returns early — skipping the critical `rsETHPrice = newRsETHPrice` assignment. After the protocol is unpaused, the stale (pre-drop, higher) `rsETHPrice` remains in storage and is immediately used by `LRTWithdrawalManager.getExpectedAssetAmount()`, causing over-commitment of `assetsCommitted` and, if `unlockQueue()` is called before the price is refreshed, over-payout to withdrawers.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` contains a downside-protection branch that pauses the deposit pool, withdrawal manager, and oracle when the computed price drops beyond the configured threshold:

```solidity
// contracts/LRTOracle.sol lines 270–282
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;   // ← early return
    }
    ...
}
...
rsETHPrice = newRsETHPrice;   // ← NEVER REACHED when isPriceDecreaseOffLimit
``` [1](#0-0) [2](#0-1) 

The `return` at line 281 exits before line 313 (`rsETHPrice = newRsETHPrice`). Consequently, `rsETHPrice` retains the pre-drop value — which is higher than the true post-slashing value — for the entire duration the protocol remains paused and beyond, until `updateRSETHPrice()` is explicitly called again after unpausing.

Both `LRTWithdrawalManager.getExpectedAssetAmount()` and `LRTDepositPool.getRsETHAmountToMint()` read `lrtOracle.rsETHPrice()` directly from storage:

```solidity
// contracts/LRTWithdrawalManager.sol line 593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [3](#0-2) 

When the admin unpauses the withdrawal manager (and deposit pool) before calling `updateRSETHPrice()`, the stale, inflated `rsETHPrice` is immediately live and usable.

---

### Impact Explanation

**Scenario A — Over-commitment (temporary fund freeze for other users):**  
A user calls `initiateWithdrawal()` while `rsETHPrice` is stale. `getExpectedAssetAmount()` returns an inflated value, which is added to `assetsCommitted[asset]`. This over-commits protocol assets, causing `getAvailableAssetAmount()` to return a deflated figure and blocking other users from initiating withdrawals until the committed amount is corrected. [4](#0-3) 

**Scenario B — Over-payout (theft of yield/assets):**  
If an operator calls `unlockQueue()` before `updateRSETHPrice()` is called, `_calculatePayoutAmount()` computes `currentReturn` using the same stale `rsETHPrice`. Since `expectedAssetAmount == currentReturn` (both derived from the stale price), the payout equals the inflated amount. Withdrawers receive more underlying assets than the actual post-slashing rsETH value entitles them to, at the expense of remaining rsETH holders. [5](#0-4) 

Impact classification: **Medium — temporary freezing of funds** (Scenario A) and **High — theft of unclaimed yield** (Scenario B).

---

### Likelihood Explanation

The trigger condition (price drop exceeding `pricePercentageLimit`) corresponds to a real-world slashing event on EigenLayer — a plausible but infrequent occurrence. The exploitation window opens whenever the admin unpauses the withdrawal manager before calling `updateRSETHPrice()`. There is no on-chain enforcement requiring `updateRSETHPrice()` to be called first; the unpause functions (`lrtOracle.unpause()`, `withdrawalManager.unpause()`) are independent transactions. A sophisticated user monitoring the mempool for unpause transactions can front-run the `updateRSETHPrice()` call. Likelihood: **Low-Medium**.

---

### Recommendation

Before the `return` statement in the `isPriceDecreaseOffLimit` branch, update `rsETHPrice` to the newly computed value so that the stored price always reflects the latest known state:

```solidity
if (isPriceDecreaseOffLimit) {
    rsETHPrice = newRsETHPrice;   // ← add this
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

Alternatively, enforce at the contract level that `updateRSETHPrice()` must be called (and succeed) before the withdrawal manager can be unpaused, or add a check in `initiateWithdrawal()` / `unlockQueue()` that reverts if `rsETHPrice` has not been updated since the last pause.

---

### Proof of Concept

1. Protocol is operating normally; `rsETHPrice = 1.05 ether`, `highestRsethPrice = 1.05 ether`, `pricePercentageLimit = 0.05e18` (5%).
2. A slashing event reduces the true ETH backing per rsETH to `0.98 ether` (a 6.7% drop, exceeding the 5% limit).
3. Anyone calls `updateRSETHPrice()`:
   - `newRsETHPrice = 0.98 ether`
   - `isPriceDecreaseOffLimit = true`
   - Deposit pool, withdrawal manager, and oracle are paused.
   - **Early return fires — `rsETHPrice` remains `1.05 ether` in storage.**
4. Admin investigates, decides the slashing is contained, and unpauses all three contracts (three separate transactions).
5. **Before** `updateRSETHPrice()` is called, an attacker calls `initiateWithdrawal(ETH, X_rsETH)`:
   - `getExpectedAssetAmount` = `X * 1.05 / 1.0` = `1.05X ETH` (stale price)
   - True entitlement = `X * 0.98 / 1.0` = `0.98X ETH`
   - `assetsCommitted[ETH] += 1.05X` (over-committed by `0.07X ETH`)
6. Operator calls `unlockQueue(ETH, ...)` (still before `updateRSETHPrice()`):
   - `_calculatePayoutAmount` uses `rsETHPrice = 1.05` → `currentReturn = 1.05X`
   - `min(1.05X, 1.05X) = 1.05X ETH` paid out
   - Attacker receives `0.07X ETH` more than their rsETH is worth, extracted from other holders. [1](#0-0) [6](#0-5) [3](#0-2) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L270-282)
```text
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
```

**File:** contracts/LRTOracle.sol (L299-315)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L168-173)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```
