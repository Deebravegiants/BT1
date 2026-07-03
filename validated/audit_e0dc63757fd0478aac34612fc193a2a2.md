### Title
Unbounded `assetsCommitted` Consumption Allows Temporary DOS of Withdrawal Initiation - (File: contracts/LRTWithdrawalManager.sol)

### Summary
Any unprivileged user holding rsETH can call `initiateWithdrawal` to increase the shared `assetsCommitted[asset]` counter without any per-user cap. An attacker with sufficient rsETH can saturate this counter up to the total protocol TVL for a given asset, causing `getAvailableAssetAmount` to return zero and reverting every subsequent `initiateWithdrawal` call from legitimate users.

### Finding Description
`initiateWithdrawal` in `LRTWithdrawalManager` gates new requests on `getAvailableAssetAmount`:

```solidity
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
```

`getAvailableAssetAmount` computes:

```solidity
uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
availableAssetAmount = totalAssets > assetsCommitted[asset]
    ? totalAssets - assetsCommitted[asset] : 0;
```

`assetsCommitted[asset]` is a single shared counter incremented by every caller. There is no per-user ceiling, no rate limit, and no cooldown. An attacker can call `initiateWithdrawal` repeatedly — each call transferring the minimum `minRsEthAmountToWithdraw[asset]` of rsETH — until `assetsCommitted[asset] ≥ totalAssets`. At that point `getAvailableAssetAmount` returns 0 and every honest user's `initiateWithdrawal` reverts with `ExceedAmountToWithdraw`.

The attacker does not permanently lose capital: after the operator calls `unlockQueue`, `assetsCommitted` is decremented for each unlocked request, and the attacker can then call `completeWithdrawal` to recover the underlying asset. The attacker can immediately re-initiate new withdrawal requests to re-saturate the counter, sustaining the DOS across multiple operator unlock cycles. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
When `assetsCommitted[asset] ≥ totalAssets`, the `initiateWithdrawal` function — the sole entry point for the standard withdrawal lifecycle — is completely blocked for all users. rsETH holders cannot begin the process of redeeming their tokens for the underlying LST or ETH. This constitutes a **temporary freezing of funds**: users' rsETH is economically stranded (cannot be redeemed) for as long as the attacker sustains the saturated state. The operator can call `unlockQueue` to partially relieve pressure, but the attacker can immediately re-saturate the counter, making the DOS persistent until the attacker voluntarily stops or is outcompeted. [4](#0-3) [5](#0-4) 

### Likelihood Explanation
The attacker must hold rsETH whose redemption value equals the total protocol TVL for the targeted asset (e.g., all ETH deposited across the deposit pool, node delegators, and unstaking vault). For a mature deployment this is a very high capital bar, making the attack expensive but not impossible for a well-capitalised adversary. The attacker recovers their capital after each withdrawal cycle, so the net cost is gas plus the opportunity cost of locking funds for the withdrawal delay (default 8 days). The attack is most feasible when protocol TVL is low (early deployment) or when targeting a lower-TVL supported LST. No privileged access is required; the entry path is fully open to any rsETH holder. [6](#0-5) [7](#0-6) 

### Recommendation
Introduce a per-user cap on the total `assetsCommitted` attributable to a single address, or enforce a maximum number of open withdrawal requests per user per asset (analogous to `maxNumberOfWithdrawalsPerUser` already present in `KernelDepositPool`). Alternatively, track each user's committed amount in a separate mapping and reject requests that would push any single user's committed share above a configurable fraction of `totalAssets`. This mirrors the recommendation in the external report: verify that the caller is a legitimate participant before allowing them to consume the shared resource. [8](#0-7) [9](#0-8) 

### Proof of Concept
1. Attacker acquires rsETH (e.g., via `LRTDepositPool.depositETH`) sufficient to cover `getAvailableAssetAmount(ETH_TOKEN)`.
2. Attacker calls `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, chunk, "")` in a loop, each time committing `chunk` worth of ETH, until `assetsCommitted[ETH_TOKEN] == totalAssets`.
3. Any honest user calling `initiateWithdrawal` now receives `ExceedAmountToWithdraw`.
4. Operator calls `unlockQueue` → `assetsCommitted` decreases for unlocked requests.
5. Attacker immediately calls `completeWithdrawal` to recover ETH, then re-deposits to obtain rsETH and repeats from step 2.
6. The withdrawal initiation path remains blocked for honest users across cycles. [10](#0-9) [11](#0-10)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-53)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L107-108)
```text
    /// @notice The maximum number of withdrawals that any user can have open (unclaimed) at any time
    uint256 public maxNumberOfWithdrawalsPerUser;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L323-323)
```text
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```
