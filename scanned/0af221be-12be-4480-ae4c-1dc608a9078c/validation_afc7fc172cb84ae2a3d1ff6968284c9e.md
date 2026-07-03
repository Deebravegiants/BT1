### Title
Automatic Pause of `LRTWithdrawalManager` Locks User rsETH With No Cancel Path; Unpause Immediately Settles Pending Requests at Depressed Price — (File: `contracts/LRTWithdrawalManager.sol`, `contracts/LRTOracle.sol`)

---

### Summary

When `LRTOracle._updateRsETHPrice()` detects a price drop beyond `pricePercentageLimit`, it automatically pauses `LRTWithdrawalManager`. Users who have already called `initiateWithdrawal` — transferring their rsETH into the contract — have no cancel mechanism and cannot recover their tokens during the pause. `unlockQueue` is also blocked by `whenNotPaused`. When the admin eventually unpauses, `unlockQueue` immediately recalculates each pending request's payout at the current (further-depressed) price via `_calculatePayoutAmount`, which returns `min(expectedAssetAmount, currentReturn)`. Users burn their full rsETH amount but receive fewer underlying assets than they were promised at initiation time, with no recourse.

---

### Finding Description

**Step 1 — User initiates withdrawal at a favorable price.**

`initiateWithdrawal` transfers the user's rsETH to the contract and records `expectedAssetAmount` at the current oracle price:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [1](#0-0) 

**Step 2 — Oracle auto-pauses `LRTWithdrawalManager`.**

`_updateRsETHPrice()` in `LRTOracle` contains a downside-protection circuit breaker. If the newly computed rsETH price falls more than `pricePercentageLimit` below `highestRsethPrice`, it calls `withdrawalManager.pause()` and returns without updating the stored price:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [2](#0-1) 

This pause is triggered permissionlessly by anyone calling the public `updateRSETHPrice()` during a market downturn. [3](#0-2) 

**Step 3 — All user-facing and operator-facing withdrawal functions are blocked.**

Both `completeWithdrawal` and `unlockQueue` carry `whenNotPaused`:

```solidity
function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused { ... }
function unlockQueue(...) external nonReentrant onlySupportedAsset(asset) whenNotPaused onlyAssetTransferOrOperatorRole { ... }
``` [4](#0-3) [5](#0-4) 

There is no `cancelWithdrawal` function anywhere in `LRTWithdrawalManager`. The user's rsETH is irrecoverably locked in the contract for the duration of the pause.

**Step 4 — Upon unpause, `unlockQueue` immediately settles at the current depressed price.**

`_unlockWithdrawalRequests` calls `_calculatePayoutAmount`, which returns `min(expectedAssetAmount, currentReturn)`:

```solidity
uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);
...
assetsCommitted[asset] -= request.expectedAssetAmount;
request.expectedAssetAmount = payoutAmount;   // overwritten to the lower value
rsETHAmountToBurn += request.rsETHUnstaked;   // full rsETH burned regardless
``` [6](#0-5) 

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
``` [7](#0-6) 

The user's entire rsETH is burned, but they receive only `currentReturn` (the lower amount). The shortfall (`expectedAssetAmount − currentReturn`) remains in the vault and is not returned to the user.

---

### Impact Explanation

**Temporary freezing of funds (Medium):** Users who have already called `initiateWithdrawal` have their rsETH locked in `LRTWithdrawalManager` with no cancel path for the entire duration of the pause. The pause has no on-chain time limit; it persists until an admin manually calls `unpause()`.

**Value loss upon unpause:** Immediately after unpause, an operator calls `unlockQueue`. Because `_calculatePayoutAmount` uses the current (depressed) price and the `min` function, users receive fewer underlying assets than they were promised at initiation time, while burning their full rsETH balance. This is a direct, irreversible loss of value caused by the pause window, not by the user's own action.

---

### Likelihood Explanation

The auto-pause trigger is permissionless — any caller of the public `updateRSETHPrice()` during a market downturn can activate it. EigenLayer slashing events, LST de-pegs, or coordinated selling of underlying assets are all realistic triggers. The pause duration is unbounded (admin-controlled unpause only). During volatile markets — exactly when users most want to exit — the mechanism locks them in and then settles them at the worst available price the moment the pause lifts.

---

### Recommendation

1. **Add a `cancelWithdrawal` function** that allows users to reclaim their rsETH while a request is still in the locked (pre-`unlockQueue`) state. This eliminates the fund-freeze impact.
2. **Introduce a grace period after unpause** before `unlockQueue` can be called, giving users time to cancel pending requests if they no longer wish to withdraw at the current price.
3. **Alternatively, snapshot the rsETH price at `initiateWithdrawal` time** and guarantee that payout is calculated at that price (not the price at `unlockQueue` time), so the pause cannot worsen the user's settlement rate.

---

### Proof of Concept

1. rsETH price is 1.05 ETH/rsETH. Alice calls `initiateWithdrawal(ETH, 100e18)`. Her 100 rsETH is transferred to `LRTWithdrawalManager`; `expectedAssetAmount` is recorded as 105 ETH.
2. A market event causes the computed rsETH price to drop to 0.90 ETH/rsETH (> `pricePercentageLimit` below `highestRsethPrice`). Any caller invokes `updateRSETHPrice()`. `LRTOracle._updateRsETHPrice()` fires `withdrawalManager.pause()` and returns without updating `rsETHPrice`.
3. Alice attempts `completeWithdrawal` → reverts (`whenNotPaused`). She attempts to cancel → no such function exists. Her 100 rsETH is frozen.
4. After an extended pause, the admin calls `unpause()` on `LRTWithdrawalManager`. The oracle price is now 0.90 ETH/rsETH.
5. An operator immediately calls `unlockQueue`. `_calculatePayoutAmount` computes `currentReturn = 100e18 * 0.90e18 / 1e18 = 90 ETH`. Since `90 < 105`, Alice's `expectedAssetAmount` is overwritten to 90 ETH and all 100 rsETH is burned.
6. Alice calls `completeWithdrawal` and receives 90 ETH — 15 ETH less than she was promised, with no ability to have cancelled during the pause.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L183-184)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
```

**File:** contracts/LRTWithdrawalManager.sol (L268-281)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
```

**File:** contracts/LRTWithdrawalManager.sol (L798-806)
```text
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L277-282)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```
