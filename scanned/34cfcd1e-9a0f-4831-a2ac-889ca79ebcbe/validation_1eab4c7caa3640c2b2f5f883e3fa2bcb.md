### Title
Missing Withdrawal Cancellation Mechanism Permanently Freezes User rsETH When Vault Is Insolvent - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal()` transfers rsETH from the user into the contract and permanently increments `assetsCommitted[asset]`. There is no `cancelWithdrawal()` function to reverse this state. The only path to release the locked rsETH is through the operator-gated `unlockQueue()` → user-called `completeWithdrawal()` sequence. If the `LRTUnstakingVault` balance is insufficient to cover committed payouts — a realistic outcome after EigenLayer slashing — the sequential unlock loop breaks at the first under-funded request, the `assetsCommitted` counter is never decremented, and all affected users' rsETH is frozen inside the contract indefinitely with no on-chain remediation path.

---

### Finding Description

`initiateWithdrawal()` performs three irreversible state mutations:

1. Transfers rsETH from the caller into the contract.
2. Computes `expectedAssetAmount` and adds it to `assetsCommitted[asset]`.
3. Pushes a `WithdrawalRequest` struct into the per-user `userAssociatedNonces` queue. [1](#0-0) 

`assetsCommitted[asset]` is **only ever decremented** inside `_unlockWithdrawalRequests()`, which is called exclusively from `unlockQueue()`: [2](#0-1) 

The unlock loop is strictly sequential (`nextLockedNonce` advances one-by-one) and breaks immediately when the vault's current balance is insufficient to cover the front-of-queue request: [3](#0-2) 

`totalAvailableAssets` is sourced from `unstakingVault.balanceOf(asset)` — the real-time vault balance, not a protocol-wide accounting figure: [4](#0-3) 

There is **no `cancelWithdrawal()`, no `rescueTokens()`, and no admin sweep for rsETH** in the contract. `sweepRemainingAssets()` only handles non-rsETH asset surpluses and is gated on `hasUnlockedWithdrawals(asset) == false`: [5](#0-4) 

`PubkeyRegistry` presents the same structural pattern — `addPubkey()` and `addPubkeys()` permanently set entries to `true` with no `removePubkey()` counterpart — but its impact is bounded to individual validator keys. The withdrawal manager issue affects all users whose requests are behind a blocked nonce. [6](#0-5) 

---

### Impact Explanation

When EigenLayer slashing reduces the assets that flow back into `LRTUnstakingVault`, the vault balance falls below the sum of `expectedAssetAmount` values for queued requests. The sequential unlock loop breaks at `nextLockedNonce` without decrementing `assetsCommitted`. Because `getAvailableAssetAmount` returns `totalAssets - assetsCommitted`, and `assetsCommitted` is now stuck at an elevated value, new `initiateWithdrawal()` calls also revert with `ExceedAmountToWithdraw`. The contract holds rsETH that is neither burned nor returnable. All affected users experience a **temporary-to-permanent freeze of their rsETH**, matching the "Temporary freezing of funds" (Medium) impact tier, escalating to "Permanent freezing of funds" (Critical) if slashing is severe enough that the vault can never be replenished to cover the committed amounts.

---

### Likelihood Explanation

EigenLayer slashing is an explicitly accepted protocol risk — the entire purpose of `NodeDelegator` is to restake assets in EigenLayer strategies and native EigenPods. The `LRTUnstakingVault` is the sole source of assets for `unlockQueue`. Any slashing event that reduces the completed-withdrawal proceeds below the sum of `expectedAssetAmount` values for pending requests triggers the freeze. This is not a theoretical edge case; it is the exact scenario the protocol's withdrawal system must be able to handle gracefully.

---

### Recommendation

1. **Add a `cancelWithdrawal(address asset)` function** that allows a user to pop their oldest pending (locked) request, decrement `assetsCommitted[asset]` by `request.expectedAssetAmount`, and return the held rsETH to the user.
2. Alternatively, expose an **admin-callable `forceUnlockRequest(address asset, uint256 nonce, uint256 reducedPayout)`** that can unlock a specific nonce with a slashing-adjusted payout, unblocking the sequential queue without requiring full asset coverage.
3. Consider adding a **`rescueRsETH()` emergency function** (gated to `PAUSER_ROLE`) that can return rsETH to users whose requests have been waiting beyond a configurable timeout with no unlock progress.

---

### Proof of Concept

```
1. Alice calls initiateWithdrawal(stETH, 10e18 rsETH).
   → 10e18 rsETH transferred to LRTWithdrawalManager.
   → assetsCommitted[stETH] += expectedAssetAmount (e.g., 10.5 stETH).
   → WithdrawalRequest stored at nonce N; nextLockedNonce[stETH] = N.

2. EigenLayer slashing event: NodeDelegator's stETH strategy shares are slashed 20%.
   → completeUnstaking() delivers only 8.4 stETH to LRTUnstakingVault instead of 10.5.

3. Operator calls unlockQueue(stETH, N+1, ...).
   → _createUnlockParams: totalAvailableAssets = unstakingVault.balanceOf(stETH) = 8.4 stETH.
   → _unlockWithdrawalRequests: payoutAmount for nonce N = min(10.5, currentReturn) = 10.5 stETH.
   → 8.4 < 10.5 → break. nextLockedNonce[stETH] unchanged at N.
   → assetsCommitted[stETH] NOT decremented.

4. Alice calls completeWithdrawal(stETH) → reverts: WithdrawalLocked (nonce N >= nextLockedNonce N).

5. Alice has no cancelWithdrawal() to call. Her 10e18 rsETH is stuck in the contract.
   getAvailableAssetAmount(stETH) = totalAssets - assetsCommitted = near-zero or zero.
   New withdrawal requests by other users also revert: ExceedAmountToWithdraw.
``` [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** contracts/LRTWithdrawalManager.sol (L700-717)
```text
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
```

**File:** contracts/LRTWithdrawalManager.sol (L800-815)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

            unlockedWithdrawalsCount[asset]++;

            unchecked {
                nextLockedNonce_++;
            }
        }
        nextLockedNonce[asset] = nextLockedNonce_;
```

**File:** contracts/LRTWithdrawalManager.sol (L846-851)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```

**File:** contracts/PubkeyRegistry.sol (L41-49)
```text
    function addPubkey(bytes calldata pubkey) external onlyLRTNodeDelegator {
        pubkeyRegistry[keccak256(pubkey)] = true;
    }

    function addPubkeys(bytes[] calldata pubkeys) external onlyLRTManager {
        for (uint256 i = 0; i < pubkeys.length; i++) {
            pubkeyRegistry[keccak256(pubkeys[i])] = true;
        }
    }
```
