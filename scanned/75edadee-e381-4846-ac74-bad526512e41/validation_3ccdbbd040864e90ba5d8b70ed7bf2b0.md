### Title
Withdrawal Requests Cannot Be Cancelled, Permanently Inflating `assetsCommitted` and Freezing User rsETH — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` has no mechanism for a user to cancel a queued withdrawal request. Once `initiateWithdrawal` is called, the user's rsETH is transferred into the contract and `assetsCommitted[asset]` is permanently incremented until an operator calls `unlockQueue`. If the queue stalls — because the first pending request cannot be covered by available assets — every subsequent user's rsETH is also frozen, and `assetsCommitted` remains inflated, blocking all new withdrawal initiations for that asset.

---

### Finding Description

`initiateWithdrawal` transfers rsETH from the caller into the contract and records a committed asset amount: [1](#0-0) 

`assetsCommitted[asset]` is the **only** counter that gates new withdrawal requests: [2](#0-1) 

The counter is decremented in exactly one place — inside `_unlockWithdrawalRequests`, called exclusively by the operator-gated `unlockQueue`: [3](#0-2) 

The unlock loop processes requests in strict FIFO order and **breaks** the moment the first pending request cannot be covered: [4](#0-3) 

There is no `cancelWithdrawal` function anywhere in the contract or its interface: [5](#0-4) 

Consequently:
- A user who calls `initiateWithdrawal` has their rsETH locked in the contract with no recourse.
- If the head of the queue cannot be unlocked (e.g., available assets fell below the committed amount due to price movement or slashing), `nextLockedNonce` never advances, every request behind it is also frozen, and `assetsCommitted` stays inflated indefinitely.
- The inflated `assetsCommitted` causes `getAvailableAssetAmount` to return zero or near-zero, blocking all subsequent `initiateWithdrawal` calls for that asset.

---

### Impact Explanation

**Medium — Temporary (potentially permanent) freezing of user funds.**

- Every user who has called `initiateWithdrawal` has their rsETH locked in the contract with no cancel path.
- A single large or head-of-queue request that cannot be unlocked freezes the rsETH of every user queued behind it.
- `assetsCommitted[asset]` remains inflated for all stuck requests, preventing any new user from initiating a withdrawal for that asset until the queue is manually cleared by an operator — which itself requires sufficient assets to be present.

---

### Likelihood Explanation

**Medium.** Any user can call `initiateWithdrawal` at any time. The queue stall condition (available assets < committed amount for the head request) is reachable through ordinary market price movement between the time a request is queued and the time `unlockQueue` is called, or through partial slashing of underlying EigenLayer positions. No privileged action is required to trigger the freeze; the absence of a cancel function means the user has no self-help remedy.

---

### Recommendation

1. **Add a `cancelWithdrawal` function** that allows a user to remove their own pending (not yet unlocked) request, return their rsETH, and decrement `assetsCommitted[asset]` by the corresponding `expectedAssetAmount`.
2. Ensure cancellation is only permitted while the request is still in the locked (pre-`nextLockedNonce`) state, to avoid interfering with already-unlocked requests.
3. Optionally, add an expiry block to `WithdrawalRequest` so that stale requests can be pruned automatically.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(stETH, 100e18, "")`.
   - 100 rsETH is transferred from Alice to `LRTWithdrawalManager`.
   - `assetsCommitted[stETH] += X` (where X is the stETH equivalent at current price).
   - `getAvailableAssetAmount(stETH)` decreases by X for all other users.

2. The stETH price rises 20 %. Alice now wants to cancel and keep her rsETH. There is no `cancelWithdrawal` function — Alice's rsETH is locked.

3. Meanwhile, Bob calls `initiateWithdrawal(stETH, 50e18, "")`. Because `assetsCommitted` is already inflated by Alice's request, Bob's call may revert with `ExceedAmountToWithdraw` even though the protocol holds sufficient total assets.

4. The operator calls `unlockQueue(stETH, ...)`. If the available assets in `LRTUnstakingVault` have dropped below Alice's committed amount (e.g., due to slashing), the loop at line 800 breaks immediately:
   ```solidity
   if (availableAssetAmount < payoutAmount) break;
   ```
   `nextLockedNonce` does not advance. Alice's rsETH and Bob's rsETH remain locked. `assetsCommitted` stays inflated. No new withdrawals can be initiated. [6](#0-5) [7](#0-6)

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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
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

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L80-110)
```text
    // methods
    function getExpectedAssetAmount(address asset, uint256 amount) external view returns (uint256);

    function getAvailableAssetAmount(address asset) external view returns (uint256 assetAmount);

    function getUserWithdrawalRequest(
        address asset,
        address user,
        uint256 index
    )
        external
        view
        returns (uint256 rsETHAmount, uint256 expectedAssetAmount, uint256 withdrawalStartBlock, uint256 userNonce);

    function initiateWithdrawal(address asset, uint256 withdrawAmount, string calldata referralId) external;

    function completeWithdrawal(address asset, string calldata referralId) external;

    function completeWithdrawalForUser(address asset, address user, string calldata referralId) external;

    function unlockQueue(
        address asset,
        uint256 index,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked);

```
