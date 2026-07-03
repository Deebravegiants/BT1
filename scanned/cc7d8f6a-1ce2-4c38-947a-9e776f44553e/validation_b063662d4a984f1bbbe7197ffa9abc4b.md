### Title
Users Can Front-Run `updateRSETHPrice()` via `instantWithdrawal()` to Avoid Slashing Losses - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`updateRSETHPrice()` in `LRTOracle.sol` is an unrestricted public function. When a slashing event reduces underlying EigenLayer asset value, there is a window before the price is updated on-chain. During this window, any user with instant withdrawal enabled can call `instantWithdrawal()` in `LRTWithdrawalManager.sol` at the stale pre-slashing price, extracting more assets than their fair share and shifting the slashing loss entirely onto remaining rsETH holders.

---

### Finding Description

`LRTOracle.updateRSETHPrice()` carries no access control — it is callable by any address: [1](#0-0) 

When a slashing event occurs on EigenLayer, the actual ETH value backing rsETH decreases. The on-chain `rsETHPrice` state variable is only updated when `updateRSETHPrice()` (or `updateRSETHPriceAsManager()`) is called. Until that call is mined, `rsETHPrice` remains at the pre-slashing value.

`instantWithdrawal()` computes the user's payout by reading `lrtOracle.rsETHPrice()` at execution time via `getExpectedAssetAmount()`: [2](#0-1) [3](#0-2) 

There is no snapshot, no lock-in, and no minimum-of-two-prices guard in the instant withdrawal path. The user receives exactly `rsETHUnstaked * rsETHPrice / assetPrice` at the moment of execution.

The downside protection in `_updateRsETHPrice()` only pauses the protocol when the price drop **exceeds** `pricePercentageLimit`: [4](#0-3) 

For slashing events whose magnitude falls **within** `pricePercentageLimit`, the price decreases without triggering a pause. `instantWithdrawal()` carries `whenNotPaused`, so it remains fully callable throughout this window.

By contrast, the standard `initiateWithdrawal()` path is protected: `_calculatePayoutAmount()` takes the **minimum** of the originally locked `expectedAssetAmount` and the current return, so a price drop after request time reduces the payout rather than allowing the user to exit at the old rate: [5](#0-4) 

`instantWithdrawal()` has no equivalent protection.

---

### Impact Explanation

**High — Theft of unclaimed yield / avoidance of loss at the expense of other rsETH holders.**

A user who exits via `instantWithdrawal()` before `updateRSETHPrice()` is mined receives assets valued at the pre-slashing rate. The slashing loss that should have been distributed proportionally across all rsETH holders is instead concentrated on those who did not exit. The attacker's gain is a direct, quantifiable transfer of value from remaining holders.

---

### Likelihood Explanation

**Medium.**

Three conditions must hold simultaneously:
1. `isInstantWithdrawalEnabled[asset]` is `true` (a manager-controlled toggle that is expected to be enabled in normal operation).
2. A slashing event occurs whose magnitude is within `pricePercentageLimit` (i.e., does not trigger an automatic pause).
3. The attacker acts — or front-runs the `updateRSETHPrice()` mempool transaction — before the price update is mined.

Condition 3 is straightforward: `updateRSETHPrice()` is public, so its pending transaction is visible in the mempool. A monitoring bot can reliably detect the slashing event on EigenLayer and submit `instantWithdrawal()` with a higher gas price. Conditions 1 and 2 are protocol-state-dependent but represent the normal operating regime.

---

### Recommendation

1. **Snapshot the price at withdrawal initiation.** Record `rsETHPrice` when `instantWithdrawal()` is called and apply the same `min(lockedPrice, currentPrice)` logic used in `_calculatePayoutAmount()` for queued withdrawals. This ensures a price drop between observation and execution cannot be exploited.

2. **Introduce a short mandatory delay for instant withdrawals.** Even a 1–2 block delay eliminates the mempool front-run vector, since `updateRSETHPrice()` would be mined before the withdrawal completes.

3. **Restrict `updateRSETHPrice()` to authorized callers.** Making it callable only by a keeper role or the manager removes the public mempool signal that enables the front-run. The `updateRSETHPriceAsManager()` path already exists for privileged updates.

---

### Proof of Concept

```
State before slashing:
  rsETHPrice = 1.05e18 (stored in LRTOracle)
  Actual backing per rsETH = 1.02e18 (after slashing event on EigenLayer)

1. Slashing event occurs on EigenLayer. rsETHPrice is still 1.05e18 on-chain.

2. Keeper submits updateRSETHPrice() → mempool (would set rsETHPrice = 1.02e18).

3. Attacker observes the pending tx. Submits instantWithdrawal(ETH, 100e18, "")
   with higher gas, front-running the keeper.

4. instantWithdrawal() executes:
     assetAmountUnlocked = getExpectedAssetAmount(ETH, 100e18)
                         = 100e18 * 1.05e18 / 1e18   // stale price
                         = 105 ETH

5. updateRSETHPrice() mines next:
     rsETHPrice = 1.02e18

6. Fair payout at correct price = 100e18 * 1.02e18 / 1e18 = 102 ETH.

Attacker extracted 105 ETH instead of 102 ETH.
Excess 3 ETH is borne by remaining rsETH holders.
```

The attacker's rsETH is burned at line 229, so the supply decreases while the vault pays out at the inflated rate, permanently diluting the remaining holders' claims. [6](#0-5) [1](#0-0)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

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

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
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
