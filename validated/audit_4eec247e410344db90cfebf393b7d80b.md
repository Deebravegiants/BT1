Audit Report

## Title
Withdrawal Payout Capped at Initiation-Time Rate, Stripping Yield Accrued During Delay — (File: contracts/LRTWithdrawalManager.sol)

## Summary
`_calculatePayoutAmount()` returns `min(expectedAssetAmount, currentReturn)`. When rsETH appreciates between `initiateWithdrawal` and `unlockQueue`, the user's full rsETH is burned but they receive only the initiation-time asset equivalent. The delta — representing yield accrued on the rsETH during the mandatory delay — remains in the unstaking vault and is redistributed to remaining rsETH holders, constituting systematic theft of unclaimed yield from every withdrawer.

## Finding Description
**Step 1 — `initiateWithdrawal` (L162–175):**
The user transfers `rsETHUnstaked` to the contract. `expectedAssetAmount` is computed at the current oracle price and stored in `WithdrawalRequest.expectedAssetAmount`; `assetsCommitted[asset]` is incremented by this amount. [1](#0-0) 

**Step 2 — `unlockQueue` → `_unlockWithdrawalRequests` → `_calculatePayoutAmount` (L797–835):**
At unlock time, `_calculatePayoutAmount` computes `currentReturn = rsETHUnstaked * rsETHPrice_T1 / assetPrice_T1` and returns `min(expectedAssetAmount, currentReturn)`. [2](#0-1) 

When rsETH has appreciated (`rsETHPrice_T1 > rsETHPrice_T0`), `currentReturn > expectedAssetAmount`, so `payoutAmount = expectedAssetAmount`. The request's `expectedAssetAmount` is overwritten with this lower value (L804), and the full `rsETHUnstaked` is queued for burning (L305). [3](#0-2) 

**Step 3 — `completeWithdrawal` → `_processWithdrawalCompletion` (L734):**
The user receives `request.expectedAssetAmount` — the initiation-time amount — not the current market value of the rsETH they surrendered. [4](#0-3) 

The rsETH burned at L305 is worth `currentReturn` in assets, but only `expectedAssetAmount` leaves the vault. The difference `currentReturn - expectedAssetAmount` remains in the vault, accruing to remaining rsETH holders. No existing check prevents this: the `assetsCommitted` accounting is internally consistent (it was only ever incremented by `expectedAssetAmount`), so the solvency guard at L800 does not protect the user's yield. [5](#0-4) 

## Impact Explanation
**High — Theft of unclaimed yield.** Every withdrawer loses the staking yield that accrued on their rsETH during the mandatory delay. rsETH is a continuously yield-bearing token (~4–5% APY). Over the default 8-day delay (`withdrawalDelayBlocks = 8 days / 12 seconds`, L94), rsETH appreciates by ~0.09–0.11%. For a 100 ETH withdrawal, this is ~0.1 ETH of yield silently stripped per withdrawal. The stolen yield is not destroyed — it remains in the vault and benefits remaining rsETH holders. This matches the allowed impact "High. Theft of unclaimed yield." [6](#0-5) 

## Likelihood Explanation
**High.** rsETH accrues staking yield continuously via oracle price updates. Any `unlockQueue` call made after even a single oracle price update following `initiateWithdrawal` triggers the loss. The 8-day default delay (up to 16 days maximum) makes it virtually certain that rsETH will have appreciated for every withdrawal. No attacker, special conditions, or external dependencies are required — the loss occurs automatically for every normal user withdrawal. [7](#0-6) 

## Recommendation
Replace the `min()` with `currentReturn` so users receive the full current value of their rsETH at unlock time:

```solidity
function _calculatePayoutAmount(
    WithdrawalRequest storage request,
    uint256 rsETHPrice,
    uint256 assetPrice
) private view returns (uint256) {
    return (request.rsETHUnstaked * rsETHPrice) / assetPrice;
}
```

If the vault may be insolvent relative to the appreciated value, the excess rsETH should be returned to the user rather than burned, or the `assetsCommitted` accounting should be updated at unlock time to reflect the appreciated commitment. The current design silently captures the yield delta without any documented rationale or user disclosure.

## Proof of Concept
1. rsETH price at T0: `1.050e18`. stETH price: `1.000e18`.
2. User calls `initiateWithdrawal(stETH, 100e18)`.
   - `expectedAssetAmount = 100e18 * 1.050e18 / 1.000e18 = 105e18` stETH stored.
   - 100 rsETH transferred to contract.
3. 8 days pass. Oracle updates rsETH price to `1.051e18` (~one day of 4.5% APY yield).
4. Operator calls `unlockQueue(stETH, ...)`.
   - `currentReturn = 100e18 * 1.051e18 / 1.000e18 = 105.1e18`.
   - `_calculatePayoutAmount` returns `min(105e18, 105.1e18) = 105e18`.
   - `request.expectedAssetAmount` set to `105e18`. 100 rsETH burned.
5. User calls `completeWithdrawal(stETH)`.
   - User receives `105e18` stETH.
   - **Lost yield: `0.1e18` stETH** remains in vault for other rsETH holders.

**Foundry test plan:** Deploy contracts on a mainnet fork. Call `initiateWithdrawal`. Advance blocks past `withdrawalDelayBlocks`. Mock oracle to return a higher rsETH price. Call `unlockQueue`. Assert `request.expectedAssetAmount == 105e18` (not `105.1e18`). Assert user balance after `completeWithdrawal` equals `105e18`, confirming `0.1e18` yield was stripped.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L305-305)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
```

**File:** contracts/LRTWithdrawalManager.sol (L338-343)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
```

**File:** contracts/LRTWithdrawalManager.sol (L734-734)
```text
        _transferAsset(asset, user, request.expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L802-807)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;
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
