### Title
Unbounded withdrawal queue flooding via uncapped `initiateWithdrawal` requests causes temporary freezing of legitimate user funds - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.initiateWithdrawal` imposes no per-user cap on the number of pending withdrawal requests and defaults `minRsEthAmountToWithdraw[asset]` to zero, allowing any rsETH holder to flood the global FIFO withdrawal queue with dust requests. Because `_unlockWithdrawalRequests` must advance `nextLockedNonce` sequentially through every queued entry before reaching later requests, legitimate users whose requests are enqueued after the attacker's are temporarily frozen until the operator exhausts the entire backlog.

### Finding Description
`initiateWithdrawal` accepts any `rsETHUnstaked >= 1 wei` when `minRsEthAmountToWithdraw[asset]` has not been explicitly set (its default value is `0`):

```solidity
// LRTWithdrawalManager.sol L162-164
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

Because `minRsEthAmountToWithdraw[asset]` is a `mapping(address => uint256)` with no initialization in `initialize()`, it is `0` for every asset until an admin explicitly calls `setMinRsEthAmountToWithdraw`. The condition `rsETHUnstaked < 0` is vacuously false for `uint256`, so only the zero-amount guard applies.

Each accepted call pushes a new nonce into the global sequence:

```solidity
// LRTWithdrawalManager.sol L756-757
userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
```

The operator's `unlockQueue` → `_unlockWithdrawalRequests` must then walk every entry in order:

```solidity
// LRTWithdrawalManager.sol L790-814
while (nextLockedNonce_ < firstExcludedIndex) {
    bytes32 requestId = getRequestId(asset, nextLockedNonce_);
    WithdrawalRequest storage request = withdrawalRequests[requestId];
    if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
    uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);
    if (availableAssetAmount < payoutAmount) break;
    ...
    unchecked { nextLockedNonce_++; }
}
nextLockedNonce[asset] = nextLockedNonce_;
```

`nextLockedNonce` is a single global cursor shared across all users for a given asset. A request at nonce `N+1` (Alice's) cannot be unlocked until `nextLockedNonce` has advanced past all nonces `0..N`. If the attacker occupies nonces `0..N` with dust requests, Alice's request at `N+1` is blocked regardless of how many batched `unlockQueue` calls the operator makes — each batch must still process attacker entries before reaching Alice's.

### Impact Explanation
Alice's withdrawal is temporarily frozen: her rsETH is already transferred into the contract at `initiateWithdrawal` time, but her request cannot be unlocked until the operator has processed every preceding attacker entry. With a large enough flood (e.g., tens of thousands of 1-wei requests), the operator must issue proportionally many `unlockQueue` batches, each consuming a full block's worth of gas, delaying Alice's access to her underlying assets for an extended and attacker-controlled period. This constitutes **temporary freezing of funds** (Medium impact per scope).

### Likelihood Explanation
rsETH is obtainable on Arbitrum via `RSETHPool` at low cost. An attacker can acquire a small rsETH balance, split it into thousands of 1-wei requests, and submit them cheaply on Arbitrum before Alice's request arrives on mainnet. The attack requires no privileged access, no oracle manipulation, and no governance capture — only a modest rsETH balance and low L2 gas fees. The attacker recovers their rsETH (minus gas) by completing their own withdrawals after the delay.

### Recommendation
1. **Short term:** Enforce a non-zero `minRsEthAmountToWithdraw` for every supported asset at initialization time (e.g., `0.01 ether` worth of rsETH). Add a per-user cap on the number of simultaneously pending withdrawal requests (e.g., `require(userAssociatedNonces[asset][msg.sender].length() < MAX_PENDING_PER_USER)`).
2. **Long term:** Consider a per-asset global queue depth limit or a fee-per-request mechanism that makes flooding economically prohibitive, analogous to the multi-queue recommendation in the reference report.

### Proof of Concept
1. `minRsEthAmountToWithdraw[stETH]` is `0` (never set after deployment).
2. Eve holds 10 000 wei of rsETH on Arbitrum (obtained via `RSETHPool`).
3. Eve calls `LRTWithdrawalManager.initiateWithdrawal(stETH, 1, "")` 10 000 times, occupying global nonces `0..9999`.
4. Alice calls `initiateWithdrawal(stETH, 1e18, "")`, receiving nonce `10000`.
5. Operator calls `unlockQueue(stETH, 500, ...)` repeatedly. Each call advances `nextLockedNonce` by at most 500 entries. After 20 full batches (20 × full-block gas), `nextLockedNonce` reaches `10000` and Alice's request is finally unlocked.
6. Alice's funds were frozen for the entire duration of those 20 operator transactions, which the attacker can extend arbitrarily by increasing the flood size. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTWithdrawalManager.sol (L786-815)
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
```
