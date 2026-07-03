### Title
Unbounded Withdrawal Request Queue Enables Spam That Causes Unbounded Gas in `_unlockWithdrawalRequests` - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal` imposes no per-user or global cap on the number of pending withdrawal requests. The internal `_unlockWithdrawalRequests` function processes them in an unbounded `while` loop. An unprivileged rsETH holder can spam the queue with minimum-sized requests, forcing the `unlockQueue` call to iterate over an arbitrarily large number of entries, consuming unbounded gas and potentially exceeding the block gas limit.

---

### Finding Description

`initiateWithdrawal` accepts any call from any rsETH holder as long as `rsETHUnstaked >= minRsEthAmountToWithdraw[asset]`. There is no check on how many pending requests a single user (or all users combined) may have outstanding:

```solidity
// contracts/LRTWithdrawalManager.sol:162-176
function initiateWithdrawal(address asset, uint256 rsETHUnstaked, ...) external ... {
    if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset])
        revert InvalidAmountToWithdraw();
    ...
    _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
}
```

Each call pushes a new nonce into `userAssociatedNonces[asset][user]` and increments the global `nextUnusedNonce[asset]`. The operator-facing `unlockQueue` then calls `_unlockWithdrawalRequests`, which iterates from `nextLockedNonce[asset]` up to the caller-supplied `firstExcludedIndex`:

```solidity
// contracts/LRTWithdrawalManager.sol:790-815
while (nextLockedNonce_ < firstExcludedIndex) {
    bytes32 requestId = getRequestId(asset, nextLockedNonce_);
    WithdrawalRequest storage request = withdrawalRequests[requestId];

    if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

    uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);
    if (availableAssetAmount < payoutAmount) break;

    assetsCommitted[asset] -= request.expectedAssetAmount;
    request.expectedAssetAmount = payoutAmount;
    rsETHAmountToBurn += request.rsETHUnstaked;
    availableAssetAmount -= payoutAmount;
    assetAmountToUnlock += payoutAmount;
    unlockedWithdrawalsCount[asset]++;
    unchecked { nextLockedNonce_++; }
}
```

Each iteration performs multiple storage reads and writes (`withdrawalRequests`, `assetsCommitted`, `unlockedWithdrawalsCount`). With thousands of spam entries, a single `unlockQueue` call can exhaust the block gas limit.

Contrast this with `KernelDepositPool`, which explicitly guards against this pattern:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:323
if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser)
    revert WithdrawalLimitReached();
```

`LRTWithdrawalManager` has no equivalent guard.

---

### Impact Explanation

**Medium — Unbounded gas consumption.**

If an attacker floods the queue with enough minimum-sized withdrawal requests, any single `unlockQueue` call that attempts to cover a large nonce range will exceed the block gas limit and revert. The operator is forced to process in ever-smaller batches, and if the attacker continuously re-fills the queue, the effective throughput of the withdrawal system is throttled to near zero. Legitimate users' withdrawal requests pile up behind the spam entries and cannot be unlocked in a timely manner, constituting a temporary freeze of funds for those users.

---

### Likelihood Explanation

**Medium.** Any rsETH holder can execute this attack. The only cost is the gas for each `initiateWithdrawal` call and the rsETH locked per request (which is returned when the request is eventually processed). The attacker does not lose funds; they merely lock them temporarily. The minimum withdrawal amount (`minRsEthAmountToWithdraw`) is the only throttle, and it can be set to a low value. The attack is repeatable across blocks.

---

### Recommendation

1. **Add a per-user pending-request cap** in `initiateWithdrawal`, analogous to `KernelDepositPool.maxNumberOfWithdrawalsPerUser`:
   ```solidity
   if (userAssociatedNonces[asset][msg.sender].length() >= maxPendingWithdrawalsPerUser)
       revert TooManyPendingWithdrawals();
   ```
2. **Add a gas guard or iteration cap** inside `_unlockWithdrawalRequests` so a single call cannot iterate more than a protocol-defined maximum number of entries regardless of `firstExcludedIndex`.
3. Consider a **minimum rsETH amount** that is economically meaningful to deter low-cost spam.

---

### Proof of Concept

1. Attacker holds or acquires a small amount of rsETH (e.g., 10 × `minRsEthAmountToWithdraw`).
2. Attacker calls `initiateWithdrawal(asset, minRsEthAmountToWithdraw, "")` in a loop across many blocks, creating N requests (N can be in the thousands across multiple addresses or a single address).
3. After `withdrawalDelayBlocks` pass, the operator calls `unlockQueue(asset, nextUnusedNonce[asset], ...)` to process all pending requests.
4. The `_unlockWithdrawalRequests` while-loop iterates N times, each iteration performing multiple SLOAD/SSTORE operations.
5. For sufficiently large N, the transaction reverts with out-of-gas, and no legitimate withdrawal can be unlocked in that call.
6. The operator must split into tiny batches; the attacker re-spams between batches, keeping the queue perpetually congested. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTWithdrawalManager.sol (L744-760)
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

        emit AssetWithdrawalQueued(msg.sender, asset, rsETHUnstaked, nextUnusedNonce_);
    }
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-338)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

        // Create a withdrawal record
        uint256 withdrawalId = ++withdrawalCounter;
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
        userWithdrawalIds[msg.sender].push(withdrawalId);

        emit WithdrawalInitiated(msg.sender, _amount, withdrawalId, unlockTime);
    }
```
