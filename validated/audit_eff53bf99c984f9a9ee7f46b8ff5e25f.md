### Title
ETH Withdrawal Push-Transfer to Contract Recipient Can Permanently Freeze User Funds - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
`LRTWithdrawalManager` uses a per-user FIFO queue (`userAssociatedNonces`) to track withdrawal requests. When completing a withdrawal, the contract pushes ETH directly to the recipient via an uncapped `call`. If the recipient is a smart-contract address that reverts on ETH receipt, the entire `_processWithdrawalCompletion` call reverts, the queue pointer is never advanced, and all of that user's queued withdrawals are permanently frozen with no admin rescue path.

### Finding Description
`_processWithdrawalCompletion` is the single code path that finalises both `completeWithdrawal` (user-initiated) and `completeWithdrawalForUser` (operator-initiated). It pops the front of the user's FIFO deque, then calls `_transferAsset`:

```solidity
// contracts/LRTWithdrawalManager.sol:705
uint256 usersFirstWithdrawalRequestNonce =
    userAssociatedNonces[asset][user].popFront();
...
unlockedWithdrawalsCount[asset]--;   // line 717 – before the transfer
...
_transferAsset(asset, user, request.expectedAssetAmount); // line 734
```

`_transferAsset` for ETH:

```solidity
// contracts/LRTWithdrawalManager.sol:877-879
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```

No gas cap is set on the `call`. If `user` is a contract whose `receive()` reverts (or consumes all forwarded gas), the entire transaction reverts. Because Solidity reverts all state changes, `popFront()` is undone, `unlockedWithdrawalsCount[asset]--` is undone, and the queue pointer stays at the same position. Every subsequent call to complete this user's withdrawal will hit the same stuck entry first (FIFO), so all of the user's queued withdrawals are permanently blocked.

`completeWithdrawalForUser` provides no relief because it calls the identical internal function and still pushes ETH to `user`.

There is no admin escape hatch: `sweepRemainingAssets` is gated on `!hasUnlockedWithdrawals(asset)`, which checks `unlockedWithdrawalsCount[asset] > 0`. Because the stuck request was already counted as unlocked (in `unlockQueue` → `_unlockWithdrawalRequests` → `unlockedWithdrawalsCount[asset]++`), that counter never reaches zero, so `sweepRemainingAssets` is also permanently blocked for the asset.

### Impact Explanation
Any ETH withdrawal request whose `user` field resolves to a contract that cannot receive ETH results in:
- **Permanent freezing of the user's ETH** inside `LRTWithdrawalManager` — the rsETH was already burned during `unlockQueue`, so the user has lost their rsETH and cannot recover the ETH.
- **All subsequent ETH withdrawal requests by the same user are also frozen** because the FIFO queue always presents the stuck entry first.
- **`unlockedWithdrawalsCount[ETH]` is permanently inflated**, blocking `sweepRemainingAssets` for the ETH asset across the entire protocol.

This satisfies the **Critical – Permanent freezing of funds** impact tier.

### Likelihood Explanation
Smart-contract wallets (Gnosis Safe, Argent, account-abstraction wallets) are the primary users of DeFi protocols and routinely initiate withdrawals. A wallet can lose the ability to receive ETH if:
- All signers lose access (key loss, death, legal seizure).
- The wallet is upgraded to a version that lacks a `receive()` function.
- The wallet's `receive()` is intentionally or accidentally made to revert.

No privileged role, oracle manipulation, or external protocol compromise is required. Any depositor who used a smart-contract address to call `initiateWithdrawal` is a potential victim.

### Recommendation
Replace the push-payment pattern with a pull-payment (credit) pattern: instead of calling `_transferAsset` inside `_processWithdrawalCompletion`, record the owed amount in a `mapping(address => uint256) pendingETH` and let users call a separate `claimETH()` function. This is the exact mitigation recommended in the referenced report ("credit the user a balance they can withdraw later").

Alternatively, wrap the `_transferAsset` call in a try/catch and, on failure, credit the amount to a claimable balance rather than reverting.

### Proof of Concept
1. Deploy `VictimWallet` — a proxy contract whose `receive()` initially succeeds.
2. From `VictimWallet`, call `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager`; a withdrawal request is queued.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. `_unlockWithdrawalRequests` advances `nextLockedNonce`, sets `request.expectedAssetAmount`, increments `unlockedWithdrawalsCount[ETH]`, and burns the rsETH. The ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`.
4. Upgrade `VictimWallet`'s implementation so `receive()` reverts (or simply brick the wallet).
5. Call `completeWithdrawal(ETH_TOKEN, "")` from `VictimWallet` — reverts with `EthTransferFailed`.
6. Operator calls `completeWithdrawalForUser(ETH_TOKEN, VictimWallet, "")` — also reverts with `EthTransferFailed`.
7. The ETH sits in `LRTWithdrawalManager` forever. `unlockedWithdrawalsCount[ETH]` remains > 0, blocking `sweepRemainingAssets`. The user's rsETH is already burned and unrecoverable.

**Key lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L49-50)
```text
    mapping(address asset => mapping(address user => DoubleEndedQueue.Uint256Deque requestNonces)) public
        userAssociatedNonces;
```

**File:** contracts/LRTWithdrawalManager.sol (L192-204)
```text
    function completeWithdrawalForUser(
        address asset,
        address user,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlyLRTOperator
    {
        _processWithdrawalCompletion(asset, user, referralId);
        emit AssetWithdrawalCompletedBy(msg.sender);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L395-414)
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
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-738)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;

        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
        }

        _transferAsset(asset, user, request.expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(user, asset, request.rsETHUnstaked, request.expectedAssetAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L876-883)
```text
    function _transferAsset(address asset, address to, uint256 amount) internal {
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
        } else {
            IERC20(asset).safeTransfer(to, amount);
        }
    }
```
