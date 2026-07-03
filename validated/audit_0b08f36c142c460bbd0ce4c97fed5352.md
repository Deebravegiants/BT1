### Title
`initiateWithdrawal` Reverts When `assetsCommitted >= totalAssets`, Temporarily Freezing User Funds - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.initiateWithdrawal` enforces a capacity check that prevents any new withdrawal request from being queued whenever the total committed asset amount equals or exceeds the protocol's total tracked asset deposits. Because `assetsCommitted` is only reduced when the privileged `unlockQueue` operator call is executed, users who arrive after the capacity is saturated are completely blocked from entering the withdrawal queue — their rsETH is effectively frozen until the operator acts.

### Finding Description
`initiateWithdrawal` is the sole entry point for a user to queue a withdrawal of rsETH for an underlying LST or ETH. After transferring the user's rsETH into the contract it performs:

```solidity
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
``` [1](#0-0) 

`getAvailableAssetAmount` computes:

```solidity
uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
availableAssetAmount = totalAssets > assetsCommitted[asset]
    ? totalAssets - assetsCommitted[asset]
    : 0;
``` [2](#0-1) 

`assetsCommitted[asset]` grows with every successful `initiateWithdrawal` call and is only reduced inside `_unlockWithdrawalRequests`, which is called exclusively by the privileged `unlockQueue` function:

```solidity
assetsCommitted[asset] -= request.expectedAssetAmount;
``` [3](#0-2) 

`unlockQueue` is gated behind `onlyAssetTransferOrOperatorRole`: [4](#0-3) 

The default `withdrawalDelayBlocks` is set to 8 days at initialization: [5](#0-4) 

The upper bound is 16 days: [6](#0-5) 

**Concrete freeze path:**

1. A cohort of users calls `initiateWithdrawal` until `assetsCommitted[asset]` reaches `totalAssets` (e.g., during a market stress event or coordinated exit).
2. Any subsequent user calling `initiateWithdrawal` receives `ExceedAmountToWithdraw` regardless of how much rsETH they hold.
3. `assetsCommitted` cannot decrease until the operator calls `unlockQueue`, which itself cannot be called until `withdrawalDelayBlocks` have elapsed since the oldest pending request.
4. With the default 8-day delay (and up to 16 days), latecomers are locked out of the withdrawal queue for the entire delay window — they hold rsETH but cannot initiate the exit process.

This is structurally identical to M-36: a protocol state reachable through normal user activity (saturating committed capacity) blocks the withdrawal-request mechanism, not just immediate withdrawal, for an extended and user-uncontrollable period.

### Impact Explanation
Users holding rsETH cannot queue a withdrawal request when `assetsCommitted[asset] >= totalAssets`. Because `initiateWithdrawal` is the only path to exit (both `completeWithdrawal` and `instantWithdrawal` require a prior queued request or separate instant-withdrawal enablement), affected users are temporarily unable to begin the exit process. The freeze duration is bounded by the operator's `unlockQueue` cadence plus the withdrawal delay — up to 16 days per the contract's own cap. This constitutes **temporary freezing of funds** (Medium).

### Likelihood Explanation
The scenario is reachable by any set of unprivileged depositors acting independently. During periods of high exit demand (e.g., a depeg event, EigenLayer slashing news, or a competing yield opportunity), many users will race to call `initiateWithdrawal`. Once capacity is saturated, every subsequent caller is blocked with no on-chain recourse. No admin compromise or special privilege is required to trigger the condition.

### Recommendation
Decouple the capacity check from the ability to queue a withdrawal request. Two complementary approaches:

1. **Allow over-queuing with deferred settlement:** Remove the `ExceedAmountToWithdraw` revert from `initiateWithdrawal` and instead enforce the capacity constraint inside `_unlockWithdrawalRequests`, so requests are accepted into the queue but only settled when assets become available — mirroring the Derby recommendation.
2. **Reduce `assetsCommitted` eagerly:** Allow `unlockQueue` to be called by anyone (not just the operator) once `withdrawalDelayBlocks` have elapsed, so the committed capacity is freed without depending on operator liveness.

### Proof of Concept

1. Protocol holds 1 000 ETH total (`getTotalAssetDeposits(ETH) = 1000e18`).
2. Users A–Z call `initiateWithdrawal(ETH, ...)` in sequence; after their requests are accepted, `assetsCommitted[ETH] = 1000e18`.
3. User Bob calls `initiateWithdrawal(ETH, 1e18, "")`.
4. `getAvailableAssetAmount(ETH)` returns `1000e18 - 1000e18 = 0`.
5. `expectedAssetAmount = 1e18 > 0` → transaction reverts with `ExceedAmountToWithdraw`.
6. Bob holds rsETH but cannot enter the withdrawal queue.
7. The operator cannot call `unlockQueue` until 8 days have elapsed (default `withdrawalDelayBlocks`).
8. Bob's rsETH is frozen for up to 8–16 days with no on-chain remedy. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L276-281)
```text
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
```

**File:** contracts/LRTWithdrawalManager.sol (L340-340)
```text
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
```

**File:** contracts/LRTWithdrawalManager.sol (L596-603)
```text
    /// @notice Calculates the amount of asset available for withdrawal.
    /// @param asset The asset address.
    /// @return availableAssetAmount The asset amount avaialble for withdrawal.
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L802-802)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
```
