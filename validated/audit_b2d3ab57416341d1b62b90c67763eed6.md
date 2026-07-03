### Title
Unbounded Gas in `_unlockWithdrawalRequests` Loop via Tiny Withdrawal Request Spam - (File: contracts/LRTWithdrawalManager.sol)

### Summary
Any rsETH holder can call `initiateWithdrawal()` repeatedly with the minimum allowed amount, flooding the global FIFO withdrawal queue. When the operator later calls `unlockQueue()` with a large `firstExcludedIndex` (e.g., `nextUnusedNonce[asset]`), the `_unlockWithdrawalRequests` while-loop iterates through every attacker-inserted request, consuming O(N) gas. With enough spam entries, the loop exhausts the block gas limit, causing `unlockQueue()` to revert and temporarily freezing all legitimate users' withdrawals.

### Finding Description

`initiateWithdrawal()` is open to any rsETH holder and enforces only a configurable minimum (`minRsEthAmountToWithdraw[asset]`), which defaults to zero: [1](#0-0) 

Each call pushes a new entry into the global sequential queue via `_addUserWithdrawalRequest()`, incrementing `nextUnusedNonce[asset]`: [2](#0-1) 

The operator-facing `unlockQueue()` delegates to `_unlockWithdrawalRequests()`, which iterates from `nextLockedNonce` up to `firstExcludedIndex`. The code caps `firstExcludedIndex` at `nextUnusedNonce[asset]`, so passing `type(uint256).max` causes the loop to span the entire queue: [3](#0-2) 

The only early-exit conditions inside the loop are:
1. The withdrawal delay has not yet passed (`break` at line 795).
2. Available assets are exhausted (`break` at line 800).

Because each attacker request commits only a tiny `expectedAssetAmount`, condition 2 does not trigger early. Once the delay passes, the loop must visit every attacker-inserted entry before reaching legitimate users' requests, consuming ~3 SSTOREs + 1 SLOAD per iteration (~60 k gas each). At the Ethereum block gas limit (~30 M gas), roughly 500 iterations fit per call. An attacker who queues tens of thousands of tiny requests makes a single-call full-queue unlock impossible.

### Impact Explanation

- **Temporary freezing of funds (Medium)**: Legitimate users' withdrawal requests sit behind the attacker's entries in the FIFO queue. `completeWithdrawal()` checks `usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]` and reverts if the request has not been unlocked. Until the operator processes all attacker entries (requiring many batched `unlockQueue()` calls), legitimate users cannot complete their withdrawals. [4](#0-3) 

- **Unbounded gas consumption (Medium)**: If the operator passes a large `firstExcludedIndex`, the loop runs out of gas and reverts, blocking the unlock path entirely until the operator discovers the need to use smaller batches.

### Likelihood Explanation

- `initiateWithdrawal()` is permissionless for any rsETH holder.
- `minRsEthAmountToWithdraw[asset]` defaults to 0, making each spam entry cost only gas.
- The attacker recovers their rsETH value as the underlying asset after the delay, so the net financial cost is only gas fees.
- The attack is repeatable across multiple assets.

### Recommendation

1. **Enforce a meaningful minimum withdrawal amount** for every supported asset via `setMinRsEthAmountToWithdraw`, making spam economically prohibitive.
2. **Cap the number of pending requests per user** or globally per asset to bound queue growth.
3. **Document and enforce a safe upper bound for `firstExcludedIndex`** in `unlockQueue()` so operators always process in bounded batches.
4. Consider a per-user nonce scheme that prevents one user's requests from blocking others in the global queue.

### Proof of Concept

1. Attacker deposits ETH into `LRTDepositPool.depositETH()` to receive rsETH.
2. Attacker calls `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, 1 wei, "")` 50,000 times (possible when `minRsEthAmountToWithdraw[ETH_TOKEN] == 0`). Each call increments `nextUnusedNonce[ETH_TOKEN]`.
3. Legitimate users submit their own withdrawal requests (nonces 50,000+).
4. After the 8-day delay, the operator calls `unlockQueue(ETH_TOKEN, type(uint256).max, ...)`.
5. `firstExcludedIndex` is capped at `nextUnusedNonce[ETH_TOKEN]` (50,000+), and the while-loop attempts to iterate all 50,000 attacker entries.
6. The transaction runs out of gas and reverts.
7. Legitimate users' withdrawals remain locked; `completeWithdrawal()` reverts for all of them because `nextLockedNonce[ETH_TOKEN]` has not advanced. [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTWithdrawalManager.sol (L705-707)
```text
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L744-758)
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

**File:** contracts/LRTWithdrawalManager.sol (L770-816)
```text
    function _unlockWithdrawalRequests(
        address asset,
        uint256 availableAssetAmount,
        uint256 rsETHPrice,
        uint256 assetPrice,
        uint256 firstExcludedIndex
    )
        internal
        returns (uint256 rsETHAmountToBurn, uint256 assetAmountToUnlock)
    {
        // Check that upper limit is in the range of existing withdrawal requests. If it is greater set it to the first
        // nonce with no withdrawal request.
        if (firstExcludedIndex > nextUnusedNonce[asset]) {
            firstExcludedIndex = nextUnusedNonce[asset];
        }

        uint256 nextLockedNonce_ = nextLockedNonce[asset];
        // Revert when trying to unlock a request that has already been unlocked
        if (nextLockedNonce_ >= firstExcludedIndex) revert NoPendingWithdrawals();

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
    }
```
