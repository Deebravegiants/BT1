### Title
Unbounded Per-User Withdrawal Requests Enable Queue-Stuffing to Temporarily Freeze Legitimate Users' Funds - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager` imposes no per-user cap on pending withdrawal requests. An attacker holding sufficient rsETH can submit an unbounded number of minimum-sized requests that occupy the front of the global FIFO queue. When the operator calls `unlockQueue`, the attacker's requests consume all available asset liquidity in strict nonce order, preventing legitimate users' requests at higher nonces from being unlocked and temporarily freezing their funds.

---

### Finding Description

`initiateWithdrawal` only enforces a minimum rsETH amount per request; it places no ceiling on how many requests a single address may have in flight: [1](#0-0) 

Each call pushes a new entry into the global sequential queue via `_addUserWithdrawalRequest`, which increments the shared `nextUnusedNonce[asset]` counter: [2](#0-1) 

`_unlockWithdrawalRequests` then processes requests in strict FIFO order, breaking as soon as `availableAssetAmount` is exhausted: [3](#0-2) 

Because the loop always starts from `nextLockedNonce[asset]` (the oldest unprocessed request) and breaks the moment assets run out, an attacker who occupies the front of the queue with many small requests will consume the entire available liquidity before any later legitimate request can be unlocked.

Contrast this with `KernelDepositPool`, which explicitly caps per-user pending withdrawals: [4](#0-3) 

`LRTWithdrawalManager` has no equivalent guard.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

Legitimate users who submitted withdrawal requests after the attacker cannot have their requests unlocked until the attacker's entire batch is processed and additional asset liquidity is made available. During this window their rsETH is already burned/held by the contract and the underlying asset is inaccessible. The attacker recovers their own assets after their requests complete and can repeat the attack with the same capital indefinitely.

---

### Likelihood Explanation

**Medium.** The attacker must hold `N × minRsEthAmountToWithdraw[asset]` rsETH and pay gas for N transactions. However:
- `minRsEthAmountToWithdraw` can be zero (it is admin-settable and defaults to 0 at initialization), making the capital cost negligible.
- The attacker recovers full value after each cycle, so the attack is self-funding and repeatable.
- No special role or privileged access is required; `initiateWithdrawal` is open to any rsETH holder. [5](#0-4) 

---

### Recommendation

1. **Add a per-user pending-request cap** in `initiateWithdrawal`, analogous to `KernelDepositPool.maxNumberOfWithdrawalsPerUser`:

```solidity
uint256 public maxWithdrawalsPerUser;

// in initiateWithdrawal:
if (userAssociatedNonces[asset][msg.sender].length() >= maxWithdrawalsPerUser)
    revert TooManyPendingWithdrawals();
```

2. **Set a non-zero `minRsEthAmountToWithdraw`** for every supported asset to raise the capital cost of queue-stuffing.

3. Consider allowing `unlockQueue` to skip a configurable number of requests per address so a single spammer cannot stall the entire queue indefinitely.

---

### Proof of Concept

```
Setup:
  - minRsEthAmountToWithdraw[ETH] = 0 (default)
  - withdrawalDelayBlocks = 8 days / 12 s ≈ 57,600 blocks
  - Attacker holds 1 rsETH, split across N dust requests

Step 1: Attacker calls initiateWithdrawal(ETH, 1 wei, "") × N times.
        → nextUnusedNonce[ETH] advances by N; attacker occupies nonces [0, N-1].

Step 2: Legitimate user calls initiateWithdrawal(ETH, largeAmount, "").
        → Assigned nonce N.

Step 3: After 57,600 blocks, operator calls unlockQueue(ETH, N+1, ...).

Step 4: _unlockWithdrawalRequests loops from nonce 0 to N-1.
        Each iteration deducts 1 wei from availableAssetAmount.
        After N iterations, availableAssetAmount < largeAmount → loop breaks.
        nextLockedNonce[ETH] = N (legitimate user's request still locked).

Step 5: Attacker calls completeWithdrawal(ETH, "") × N times, recovering assets.

Step 6: Repeat from Step 1. Legitimate user's request remains permanently delayed
        until the attacker stops or the operator sources additional liquidity.
``` [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-35)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L323-323)
```text
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```
