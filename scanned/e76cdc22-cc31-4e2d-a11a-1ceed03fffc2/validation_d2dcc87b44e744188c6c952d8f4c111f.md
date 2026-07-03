### Title
DoS: Attacker May Significantly Increase the Cost of `sweepRemainingAssets()` by Creating a Large Number of Tiny Withdrawal Requests — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`minRsEthAmountToWithdraw` defaults to `0` for every asset, allowing any user to call `initiateWithdrawal` with as little as 1 wei of rsETH. An attacker can flood the withdrawal queue with an arbitrarily large number of dust requests. Because `sweepRemainingAssets` is gated on `unlockedWithdrawalsCount[asset] == 0`, and because each unlocked request can only be retired one-at-a-time via `completeWithdrawal` / `completeWithdrawalForUser`, the manager is forced to pay O(N) gas across O(N) transactions before the sweep can proceed. The same dust queue also forces the operator to iterate through every entry inside `_unlockWithdrawalRequests`, consuming unbounded gas per `unlockQueue` call.

---

### Finding Description

**Root cause — no enforced minimum withdrawal amount**

`minRsEthAmountToWithdraw` is a plain mapping whose default value is `0`: [1](#0-0) 

The guard in `initiateWithdrawal` is:

```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
``` [2](#0-1) 

When `minRsEthAmountToWithdraw[asset] == 0` (the default), the condition `rsETHUnstaked < 0` is vacuously false for `uint256`, so the only effective check is `rsETHUnstaked == 0`. Any amount ≥ 1 wei of rsETH is accepted.

**Queue inflation**

Each accepted call to `initiateWithdrawal` appends a new entry to the global FIFO queue and increments `nextUnusedNonce[asset]`: [3](#0-2) 

An attacker who holds rsETH (obtained by depositing ETH/LST into `LRTDepositPool`) can call `initiateWithdrawal` N times with 1 wei of rsETH each time. With 1 ETH deposited they receive ≈ 1e18 rsETH, theoretically enabling up to 1e18 dust requests before `assetsCommitted` saturates `getAvailableAssetAmount`. Even a few thousand requests is sufficient to cause the impacts below.

**Impact 1 — `_unlockWithdrawalRequests` unbounded while-loop**

`unlockQueue` calls `_unlockWithdrawalRequests`, which iterates from `nextLockedNonce` to `firstExcludedIndex`: [4](#0-3) 

Each iteration performs multiple storage reads and writes (`withdrawalRequests`, `assetsCommitted`, `unlockedWithdrawalsCount`). With N dust entries, the operator must either (a) pass a large `firstExcludedIndex` and risk hitting the block gas limit, or (b) make O(N) separate `unlockQueue` calls, each paying gas.

**Impact 2 — `sweepRemainingAssets` permanently blocked until O(N) completions**

`sweepRemainingAssets` is gated on `hasUnlockedWithdrawals(asset)`: [5](#0-4) 

`hasUnlockedWithdrawals` returns `true` whenever `unlockedWithdrawalsCount[asset] > 0`: [6](#0-5) 

`unlockedWithdrawalsCount` is incremented once per request inside `_unlockWithdrawalRequests` and decremented only inside `_processWithdrawalCompletion`: [7](#0-6) 

The attacker simply never calls `completeWithdrawal` for their dust requests. The manager's only recourse is to call `completeWithdrawalForUser` once per dust entry: [8](#0-7) 

This forces O(N) separate transactions before `sweepRemainingAssets` can execute.

---

### Impact Explanation

- **Unbounded gas consumption (Medium)**: The operator must pay O(N) gas across O(N) `unlockQueue` and/or `completeWithdrawalForUser` calls to drain the dust queue.
- **Temporary freezing of yield (Medium)**: `sweepRemainingAssets` — the mechanism for recovering residual LST balances to the treasury — is blocked for as long as any dust withdrawal remains unlocked but unclaimed.

---

### Likelihood Explanation

- Any rsETH holder can call `initiateWithdrawal` with 1 wei of rsETH at any time the contract is unpaused.
- `minRsEthAmountToWithdraw` is `0` by default and requires an explicit admin call to `setMinRsEthAmountToWithdraw` to harden; there is no initializer-time enforcement.
- The attacker's cost is proportional to N (gas for N `initiateWithdrawal` calls + 1 wei rsETH per call), while the operator's remediation cost is also O(N) but may occur at higher gas prices and requires active monitoring.

---

### Recommendation

1. **Enforce a non-zero minimum in the initializer**: Set `minRsEthAmountToWithdraw` to a meaningful floor (e.g., 0.001 rsETH) for every supported asset during `initialize`, not just via an optional admin setter.
2. **Add a per-user request cap**: Limit the number of open withdrawal requests per user (analogous to `MAX_WITHDRAWALS_PER_USER = 100` already present in `KernelDepositPool`).
3. **Batch-complete dust withdrawals**: Add an operator function that completes multiple withdrawal requests in a single call, reducing the O(N) transaction overhead.

---

### Proof of Concept

```
1. Attacker deposits 1 ETH into LRTDepositPool → receives ~1e18 rsETH.
2. Attacker calls initiateWithdrawal(ETH, 1, "") 10,000 times,
   each time locking 1 wei of rsETH.
   (minRsEthAmountToWithdraw[ETH] == 0, so no revert.)
3. After withdrawalDelayBlocks pass, operator calls unlockQueue(ETH, 10001, ...).
   _unlockWithdrawalRequests iterates 10,000 times, each doing 3+ storage ops.
   Gas cost: ~10,000 × ~5,000 gas = ~50M gas (exceeds block limit).
   Operator must split into many smaller calls.
4. unlockedWithdrawalsCount[ETH] is now 10,000.
5. Manager calls sweepRemainingAssets(ETH) → reverts: PendingWithdrawalsExist.
6. Manager must call completeWithdrawalForUser(ETH, attacker, "") 10,000 times
   before sweepRemainingAssets can succeed.
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-35)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
```

**File:** contracts/LRTWithdrawalManager.sol (L162-164)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
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

**File:** contracts/LRTWithdrawalManager.sol (L629-631)
```text
    function hasUnlockedWithdrawals(address asset) public view returns (bool hasUnlocked) {
        return unlockedWithdrawalsCount[asset] > 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L717-717)
```text
        unlockedWithdrawalsCount[asset]--;
```

**File:** contracts/LRTWithdrawalManager.sol (L744-757)
```text
    function _addUserWithdrawalRequest(address asset, uint256 rsETHUnstaked, uint256 expectedAssetAmount) internal {
        uint256 nextUnusedNonce_ = nextUnusedNonce[asset];

        // Generate a unique identifier for the new withdrawal request.
        bytes32 requestId = getRequestId(asset, nextUnusedNonce_);

        // Create and store the new withdrawal request.
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });

        // Map the user to the newly created request index and increment the nonce for future requests.
        userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
        nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
```

**File:** contracts/LRTWithdrawalManager.sol (L790-815)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

            // Calculate the amount user will receive
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

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
