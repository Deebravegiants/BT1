### Title
Unbounded Withdrawal Request Queue Allows Any rsETH Holder to Temporarily Freeze Legitimate Users' Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.initiateWithdrawal` imposes no per-user or global cap on the number of pending withdrawal requests. Any rsETH holder can flood the global FIFO queue with minimum-amount requests at lower nonces than legitimate users. Because `completeWithdrawal` enforces that a request's nonce must be below `nextLockedNonce[asset]`, and `nextLockedNonce` only advances sequentially through `unlockQueue`, legitimate users whose requests sit at higher nonces are blocked from completing withdrawals until every spam request ahead of them is processed by the operator.

### Finding Description
`initiateWithdrawal` accepts any amount ≥ `minRsEthAmountToWithdraw[asset]` and appends a new entry to the global queue by incrementing `nextUnusedNonce[asset]`: [1](#0-0) 

Each call pushes the caller's nonce into `userAssociatedNonces[asset][msg.sender]` and increments the global `nextUnusedNonce[asset]`: [2](#0-1) 

`completeWithdrawal` → `_processWithdrawalCompletion` pops the user's oldest nonce and immediately reverts if that nonce has not yet been unlocked (i.e., it is ≥ `nextLockedNonce[asset]`): [3](#0-2) 

`nextLockedNonce[asset]` only advances inside `_unlockWithdrawalRequests`, which the operator calls via `unlockQueue`. The loop is strictly sequential — it cannot skip nonces: [4](#0-3) 

There is no mechanism to skip or evict spam entries. Every request at a lower nonce must be individually processed before any request at a higher nonce becomes completable.

### Impact Explanation
Legitimate users who submitted withdrawal requests after the attacker's spam batch cannot call `completeWithdrawal` until the operator has processed every spam request ahead of them. Depending on the number of spam entries and the operator's cadence, this constitutes a **temporary freezing of funds** for affected users. The attacker recovers their rsETH value (as the underlying asset) once each spam request is unlocked and completed, making the net cost of the attack only gas fees and the opportunity cost of locking rsETH for the delay period.

**Impact: Medium — Temporary freezing of funds.**

### Likelihood Explanation
The entry point is `initiateWithdrawal`, which is callable by any address holding rsETH ≥ `minRsEthAmountToWithdraw[asset]`. No special role is required. If `minRsEthAmountToWithdraw` is set to a small value (or zero), the attacker can create thousands of requests with modest capital. Even with a non-trivial minimum, a well-capitalised attacker can create enough requests to delay withdrawals for hours or days. The attack is repeatable across multiple assets.

### Recommendation
1. Introduce a per-user cap on the number of pending (unlocked) withdrawal requests per asset (e.g., `require(userAssociatedNonces[asset][msg.sender].length() < MAX_PENDING_PER_USER)`).
2. Alternatively, implement a per-user nonce-based queue that is independent of the global unlock sequence, so that one user's spam cannot block another user's `completeWithdrawal`.
3. Consider a minimum withdrawal amount large enough to make mass spam economically prohibitive.

### Proof of Concept
1. Alice submits `initiateWithdrawal(ETH, minAmount, "")` 10,000 times, each at the minimum rsETH amount. Her requests occupy global nonces 0–9,999.
2. Bob submits `initiateWithdrawal(ETH, largeAmount, "")`. His request is at nonce 10,000.
3. The operator calls `unlockQueue` in batches. Each call advances `nextLockedNonce[ETH]` by the batch size.
4. Bob calls `completeWithdrawal(ETH, "")`. The check `usersFirstWithdrawalRequestNonce >= nextLockedNonce[ETH]` reverts because nonce 10,000 has not yet been reached.
5. Bob's funds remain locked until the operator has processed all 10,000 of Alice's spam requests. [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTWithdrawalManager.sol (L699-717)
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
