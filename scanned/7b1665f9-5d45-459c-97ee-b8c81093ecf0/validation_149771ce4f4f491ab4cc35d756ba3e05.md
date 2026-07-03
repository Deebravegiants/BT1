Let me examine the relevant contracts to trace this vulnerability path.

I have traced the full code path. Let me now deliver the analysis.

---

### Title
Stale `rsETHPrice` from Pre-Checkpoint Beacon-Chain Balance Inflates `assetsCommitted`, Temporarily Blocking New Withdrawal Initiations — (`contracts/LRTWithdrawalManager.sol`)

### Summary

`LRTOracle.rsETHPrice` is a **stored state variable** updated only when `updateRSETHPrice()` is called. Between a beacon-chain balance decrease and the finalization of the corresponding EigenLayer checkpoint, `getWithdrawableShares()` still returns the pre-decrease value, so any `updateRSETHPrice()` call in that window stores an inflated price. A user who calls `initiateWithdrawal()` during this window commits an inflated `expectedAssetAmount` into `assetsCommitted`. After the checkpoint finalizes, `getTotalAssetDeposits()` (which is computed live) drops, while `assetsCommitted` remains high. `getAvailableAssetAmount()` then returns zero, blocking all subsequent `initiateWithdrawal()` calls until `unlockQueue()` processes the inflated request — which cannot happen until the 8-day withdrawal delay passes.

### Finding Description

**Price storage vs. live computation mismatch**

`LRTOracle.rsETHPrice` is a stored `uint256`: [1](#0-0) 

It is only updated by explicit calls to `updateRSETHPrice()` / `updateRSETHPriceAsManager()`: [2](#0-1) 

`_updateRsETHPrice()` calls `_getTotalEthInProtocol()`, which calls `getTotalAssetDeposits()`, which calls `INodeDelegator.getAssetBalance()`: [3](#0-2) 

`getAssetBalance()` delegates to `NodeDelegatorHelper.getAssetBalance()`: [4](#0-3) 

`getWithdrawableShare()` calls `DelegationManager.getWithdrawableShares()`: [5](#0-4) 

EigenLayer's `getWithdrawableShares()` applies the current `beaconChainSlashingFactor`. Before a checkpoint finalizes, this factor has not yet been reduced, so the returned share count is inflated relative to the true post-checkpoint balance.

**`initiateWithdrawal()` uses the stored (potentially stale) price**

`getExpectedAssetAmount()` reads `lrtOracle.rsETHPrice()` — the stored value: [6](#0-5) 

`initiateWithdrawal()` adds this inflated amount to `assetsCommitted`: [7](#0-6) 

**`getAvailableAssetAmount()` uses a live computation**

After the checkpoint finalizes, `getTotalAssetDeposits()` (live) drops, but `assetsCommitted` remains at the inflated value: [8](#0-7) 

The result is `max(0, T_low − E_high) = 0`, so the check in `initiateWithdrawal()`: [9](#0-8) 
reverts with `ExceedAmountToWithdraw` for all subsequent callers.

**`unlockQueue()` cannot immediately clear `assetsCommitted`**

`_unlockWithdrawalRequests()` breaks out of the loop if the withdrawal delay has not passed: [10](#0-9) 

The default delay is 8 days (`8 days / 12 seconds`): [11](#0-10) 

So `assetsCommitted` cannot be reduced until the inflated request matures, freezing new withdrawal initiations for up to 8 days.

**`_calculatePayoutAmount()` does not restore `assetsCommitted` early**

When `unlockQueue()` eventually runs, it subtracts the old inflated `expectedAssetAmount` and replaces it with the lower payout: [12](#0-11) 

This is correct behavior, but it only executes after the 8-day delay.

**`pricePercentageLimit` does not fully mitigate this**

The downside-protection pause only triggers when `updateRSETHPrice()` is called post-checkpoint and the drop exceeds `pricePercentageLimit`: [13](#0-12) 

For drops within the limit (e.g., a 3% validator penalty with a 5% limit), the protocol does not pause, and the inflated `assetsCommitted` persists.

### Impact Explanation

All calls to `initiateWithdrawal()` for the affected asset revert with `ExceedAmountToWithdraw` for up to 8 days (the withdrawal delay). Users holding rsETH cannot queue new withdrawals during this window. Their rsETH is not lost, but the withdrawal path is temporarily unavailable. This matches **Medium — Temporary freezing of funds**.

### Likelihood Explanation

Beacon-chain checkpoints are a routine EigenLayer operation. Any validator balance decrease (inactivity leak, partial slash) creates this window. `updateRSETHPrice()` is a public, permissionless function that can be called by anyone at any time, including during the pre-checkpoint window. No special privileges or front-running are required; a regular user calling `initiateWithdrawal()` at the wrong moment is sufficient to trigger the freeze.

### Recommendation

1. In `initiateWithdrawal()`, compute `expectedAssetAmount` using a freshly computed price (call `_getTotalEthInProtocol()` inline or require a recent `updateRSETHPrice()` block timestamp) rather than the stored `rsETHPrice`.
2. Alternatively, add a staleness guard: revert if `rsETHPrice` was last updated more than N blocks ago.
3. Consider adding a `maximumRsEthPrice` bound to `initiateWithdrawal()` (analogous to the bounds already present in `unlockQueue()`) so users can protect themselves against stale prices.

### Proof of Concept

```
1. Fork mainnet at a block where an NDC has active beacon-chain validators.
2. Simulate a validator balance decrease (e.g., via `vm.store` on the EigenPod's balance).
3. Call `EigenPod.startCheckpoint()` — checkpoint is pending, not finalized.
4. Call `LRTOracle.updateRSETHPrice()` — stores P_high (inflated).
5. Call `LRTWithdrawalManager.initiateWithdrawal(asset, rsETHAmount, "")` — asserts
   assetsCommitted[asset] == E_high (inflated).
6. Call `EigenPod.verifyCheckpointProofs(...)` — checkpoint finalizes, slashingFactor drops.
7. Assert getTotalAssetDeposits(asset) < assetsCommitted[asset].
8. Call initiateWithdrawal() again — assert it reverts with ExceedAmountToWithdraw.
9. Assert block.number < request.withdrawalStartBlock + withdrawalDelayBlocks
   (unlockQueue cannot yet clear assetsCommitted).
```

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-281)
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
```

**File:** contracts/LRTDepositPool.sol (L450-451)
```text
            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
```

**File:** contracts/NodeDelegatorHelper.sol (L31-39)
```text
    function getAssetBalance(ILRTConfig lrtConfig, address asset) internal view returns (uint256) {
        address strategy = lrtConfig.assetStrategy(asset);
        if (strategy == address(0)) {
            return 0;
        }
        uint256 withdrawableShare = getWithdrawableShare(lrtConfig, IStrategy(strategy));

        return IStrategy(strategy).sharesToUnderlyingView(withdrawableShare);
    }
```

**File:** contracts/NodeDelegatorHelper.sol (L48-50)
```text
    {
        (withdrawableShares,) = getDelegationManager(lrtConfig).getWithdrawableShares(address(this), strategies);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L168-173)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L795-795)
```text
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```

**File:** contracts/LRTWithdrawalManager.sol (L802-804)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
```
