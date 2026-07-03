### Title
Unbounded Withdrawal Request Queue Growth Causes Temporary Freezing of Other Users' Withdrawals — (`contracts/LRTWithdrawalManager.sol`)

### Summary
Any user holding rsETH can call `initiateWithdrawal` an unlimited number of times, creating an unbounded number of entries in the global sequential withdrawal queue. Because `_unlockWithdrawalRequests` processes requests strictly in FIFO order via `nextLockedNonce[asset]`, a malicious user who front-loads the queue with many dust-sized requests forces all subsequent users' withdrawals to wait until every preceding request is processed. The operator cannot skip or reorder entries.

### Finding Description
`initiateWithdrawal` in `LRTWithdrawalManager` accepts any `rsETHUnstaked >= minRsEthAmountToWithdraw[asset]` and has no cap on how many times a single user (or any user) may call it:

```solidity
// contracts/LRTWithdrawalManager.sol L150-L178
function initiateWithdrawal(address asset, uint256 rsETHUnstaked, ...) external {
    if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset])
        revert InvalidAmountToWithdraw();
    ...
    assetsCommitted[asset] += expectedAssetAmount;
    _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
}
```

Each call pushes a new nonce into the global counter:

```solidity
// contracts/LRTWithdrawalManager.sol L756-L757
userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
```

The operator's `unlockQueue` → `_unlockWithdrawalRequests` iterates from `nextLockedNonce[asset]` to `firstExcludedIndex` in strict sequential order:

```solidity
// contracts/LRTWithdrawalManager.sol L790-L815
while (nextLockedNonce_ < firstExcludedIndex) {
    bytes32 requestId = getRequestId(asset, nextLockedNonce_);
    WithdrawalRequest storage request = withdrawalRequests[requestId];
    ...
    unchecked { nextLockedNonce_++; }
}
nextLockedNonce[asset] = nextLockedNonce_;
```

There is no mechanism to skip over a user's requests or reorder the queue. The operator must advance `nextLockedNonce[asset]` through every entry in sequence.

When `minRsEthAmountToWithdraw[asset]` is zero (the default before admin sets it), the effective minimum is 1 wei of rsETH. A user with a modest rsETH balance can create millions of dust requests, each committing 1 wei of `assetsCommitted[asset]`, until `getAvailableAssetAmount` is exhausted:

```solidity
// contracts/LRTWithdrawalManager.sol L599-L603
function getAvailableAssetAmount(address asset) public view returns (uint256) {
    uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
    availableAssetAmount = totalAssets > assetsCommitted[asset]
        ? totalAssets - assetsCommitted[asset] : 0;
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Impact Explanation
**Medium — Temporary freezing of funds.**

Legitimate users who submit withdrawal requests after the attacker's dust requests cannot have their requests unlocked until the operator has iterated through every preceding dust entry. With millions of 1-wei entries, the operator must call `unlockQueue` millions of times (each with a small `firstExcludedIndex` to avoid block gas limit issues), delaying all subsequent users' withdrawals for an extended and attacker-controlled period. Additionally, if `firstExcludedIndex` is set too aggressively, the `while` loop itself hits the block gas limit, making `unlockQueue` temporarily uncallable.

### Likelihood Explanation
**Medium.** The attack requires the attacker to hold rsETH (a real cost), but:
- `minRsEthAmountToWithdraw` defaults to 0, making the minimum effective amount 1 wei.
- Even with a non-zero minimum, a whale or a protocol participant with a moderate rsETH balance can create thousands of requests.
- The attack is permissionless and requires no special role.
- The attacker recovers their rsETH (converted to the underlying asset) when their requests are eventually processed, so the net cost is only gas.

### Recommendation
1. **Enforce a meaningful `minRsEthAmountToWithdraw`** at initialization (not zero) and prevent it from being set to zero.
2. **Cap the number of pending withdrawal requests per user per asset** (e.g., `require(userAssociatedNonces[asset][msg.sender].length() < MAX_REQUESTS_PER_USER)`).
3. Alternatively, allow the operator to **skip or cancel stale/dust requests** so the queue does not become permanently blocked by malicious entries.

### Proof of Concept
1. Admin deploys `LRTWithdrawalManager` with `minRsEthAmountToWithdraw[ETH] = 0` (default).
2. Attacker acquires 1e18 wei of rsETH (1 rsETH).
3. Attacker calls `initiateWithdrawal(ETH, 1, "")` 1e18 times in a loop (or across many transactions), each time committing 1 wei of `assetsCommitted[ETH]` and advancing `nextUnusedNonce[ETH]` by 1.
4. Legitimate user calls `initiateWithdrawal(ETH, 1 ether, "")` — this succeeds and is placed at nonce 1e18.
5. Operator calls `unlockQueue(ETH, 1000, ...)` — only nonces 0–999 are processed (all attacker dust).
6. Operator must call `unlockQueue` 1e15 more times before reaching the legitimate user's request at nonce 1e18, effectively freezing the legitimate user's withdrawal for an attacker-controlled duration. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-58)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
    uint256 public withdrawalDelayBlocks;

    // Next available nonce for withdrawal requests per asset, indicating total requests made.
    mapping(address asset => uint256 nonce) public nextUnusedNonce;

    // Next nonce for which a withdrawal request remains locked.
    mapping(address asset => uint256 requestNonce) public nextLockedNonce;

    // Mapping from a unique request identifier to its corresponding withdrawal request
    mapping(bytes32 requestId => WithdrawalRequest) public withdrawalRequests;

    // Maps each asset to user addresses, pointing to an ordered list of their withdrawal request nonces.
    // Utilizes a double-ended queue for efficient management and removal of initial requests.
    mapping(address asset => mapping(address user => DoubleEndedQueue.Uint256Deque requestNonces)) public
        userAssociatedNonces;

    // Asset amount committed to be withdrawn by users.
    mapping(address asset => uint256 amount) public assetsCommitted;

    mapping(address asset => bool) public isInstantWithdrawalEnabled;
    uint256 public instantWithdrawalFee; // Fee in basis points (1 = 0.01%)

    mapping(address asset => uint256) public unlockedWithdrawalsCount;
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

**File:** contracts/LRTWithdrawalManager.sol (L744-759)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L786-816)
```text
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
