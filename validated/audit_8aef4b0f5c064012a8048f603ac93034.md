### Title
No Emergency Recovery Mechanism for rsETH Locked in Withdrawal Queue When Asset Pathway Becomes Permanently Inaccessible - (`contracts/LRTWithdrawalManager.sol`)

### Summary

`LRTWithdrawalManager.initiateWithdrawal` transfers rsETH from the user into the contract as an escrow-like lock. The only path to recover those tokens is through the normal `unlockQueue` → `completeWithdrawal` lifecycle. There is no cancellation or emergency-recovery function. If the asset's withdrawal pathway becomes permanently inaccessible (e.g., the asset is removed from the supported list), the locked rsETH is permanently frozen with no on-chain recourse.

### Finding Description

In `LRTWithdrawalManager.initiateWithdrawal`, the user's rsETH is pulled into the contract:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

The rsETH stays in the contract until an operator calls `unlockQueue`, which burns it and releases the underlying asset. Only then can the user call `completeWithdrawal`.

`unlockQueue` is gated by the `onlySupportedAsset(asset)` modifier:

```solidity
function unlockQueue(address asset, ...) external nonReentrant onlySupportedAsset(asset) whenNotPaused onlyAssetTransferOrOperatorRole
```

If the asset is removed from the supported list in `LRTConfig` after a user has submitted a withdrawal request, `unlockQueue` permanently reverts for that asset. The withdrawal request is never advanced past `nextLockedNonce`, so `completeWithdrawal` also permanently reverts with `WithdrawalLocked`:

```solidity
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

There is no `cancelWithdrawal` function, no admin `recoverTokens` path for rsETH, and `sweepRemainingAssets` only sweeps the underlying LST/ETH balance — not the rsETH held in escrow. `LRTWithdrawalManager` does not inherit `Recoverable`.

### Impact Explanation

rsETH deposited into `LRTWithdrawalManager` via `initiateWithdrawal` is permanently frozen whenever the asset's unlock pathway is closed. The user loses their rsETH with no on-chain recovery path. This matches **Critical — Permanent freezing of funds**.

### Likelihood Explanation

Low. It requires an asset to be delisted from the supported list while withdrawal requests for that asset are still pending in the queue. This is a realistic operational scenario (e.g., an LST is deprecated, exploited, or its EigenLayer strategy is removed), analogous to the original report's scenario of a peer being removed on the destination chain after a cross-chain send is in flight.

### Recommendation

Add a `cancelWithdrawal` function that allows a user (or admin) to cancel a still-locked (not yet unlocked) withdrawal request and return the escrowed rsETH to the user. Alternatively, add an admin-only emergency recovery function for rsETH held in the contract, protected by a Timelock or Multisig, consistent with the original report's recommendation.

### Proof of Concept

1. User calls `initiateWithdrawal(stETH, 1e18, "")`. rsETH is transferred to `LRTWithdrawalManager`. [1](#0-0) 

2. Admin removes stETH from the supported asset list in `LRTConfig` (legitimate protocol action, e.g., stETH is deprecated).

3. Operator attempts `unlockQueue(stETH, ...)`. The `onlySupportedAsset(stETH)` modifier reverts because stETH is no longer supported. [2](#0-1) 

4. `nextLockedNonce[stETH]` is never advanced past the user's request nonce.

5. User calls `completeWithdrawal(stETH, "")`. `_processWithdrawalCompletion` reverts with `WithdrawalLocked` because `usersFirstWithdrawalRequestNonce >= nextLockedNonce[stETH]`. [3](#0-2) 

6. No `cancelWithdrawal` exists. `sweepRemainingAssets` only sweeps the underlying asset balance, not the rsETH held in escrow. [4](#0-3) 

7. The user's rsETH is permanently locked in `LRTWithdrawalManager` with no recovery path. [5](#0-4)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L395-413)
```text
    function sweepRemainingAssets(address asset)
        external
        nonReentrant
        onlySupportedAsset(asset)
        onlyLRTManager
        returns (uint256 transferredAmount)
    {
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();

        uint256 balance = _getAssetBalance(asset);
        if (balance == 0) revert AmountMustBeGreaterThanZero();

        // Transfer to treasury
        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        _transferAsset(asset, treasury, balance);

        emit RemainingAssetsSwept(asset, balance, treasury);
        return balance;
```

**File:** contracts/LRTWithdrawalManager.sol (L705-707)
```text
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```
