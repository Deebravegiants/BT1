### Title
Paused `LRTWithdrawalManager` Prevents Users from Completing Pending Withdrawals, Temporarily Freezing rsETH-Backed Funds - (File: contracts/LRTWithdrawalManager.sol)

### Summary
The `LRTWithdrawalManager` contract applies `whenNotPaused` to `completeWithdrawal()`, `completeWithdrawalForUser()`, and `instantWithdrawal()`. When the protocol is paused — including via the automatic price-drop circuit breaker in `LRTOracle` — users who have already burned or committed rsETH into the withdrawal queue cannot retrieve their underlying assets (ETH/LSTs) until the pause is lifted. This constitutes a temporary freeze of user funds.

### Finding Description
The `LRTWithdrawalManager` contract guards all user-facing withdrawal completion paths with `whenNotPaused`:

- `completeWithdrawal()` — line 183
- `completeWithdrawalForUser()` — line 192–200
- `instantWithdrawal()` — line 212–219

When a user calls `initiateWithdrawal()`, their rsETH is immediately transferred into the contract (`IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked)`). The rsETH is held by the contract while the request sits in the queue awaiting `unlockQueue()` and then `completeWithdrawal()`. If the contract is paused at any point after `initiateWithdrawal()` but before `completeWithdrawal()`, the user's rsETH is locked in the contract and the underlying asset cannot be claimed.

Critically, the pause can be triggered automatically — not just by an admin — via `LRTOracle._updateRsETHPrice()`, which calls `withdrawalManager.pause()` whenever the rsETH price drops beyond `pricePercentageLimit`. This is a realistic, non-admin-collusion trigger path.

Additionally, `unlockQueue()` itself is also gated by `whenNotPaused` (line 279), meaning that even the operator-side step of processing the queue is blocked during a pause, compounding the delay for users.

### Impact Explanation
Medium. When the `LRTWithdrawalManager` is paused, users who have already submitted `initiateWithdrawal()` — transferring their rsETH into the contract — cannot call `completeWithdrawal()` to receive their ETH/LST. Their rsETH is held in the contract and the underlying assets are inaccessible for the duration of the pause. This is a temporary freeze of user funds. The rsETH is not permanently lost (it is recoverable once unpaused), but users are denied access to their assets for an indefinite period.

### Likelihood Explanation
Medium. The pause is not solely admin-triggered. `LRTOracle._updateRsETHPrice()` automatically pauses `LRTWithdrawalManager` when the rsETH price drops beyond the configured `pricePercentageLimit`. Price drops of this magnitude are plausible during market stress — precisely the conditions under which users most urgently need to complete withdrawals. Any public caller of `updateRSETHPrice()` can indirectly trigger this path if the price condition is met.

### Recommendation
Remove `whenNotPaused` from `completeWithdrawal()` and `completeWithdrawalForUser()` so that users with already-queued, already-unlocked withdrawal requests can always claim their assets. The `initiateWithdrawal()` and `instantWithdrawal()` functions may reasonably remain paused to prevent new commitments during emergencies. `unlockQueue()` should similarly be callable while paused so that operator processing of the queue is not blocked.

```diff
- function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
+ function completeWithdrawal(address asset, string calldata referralId) external nonReentrant {
    _processWithdrawalCompletion(asset, msg.sender, referralId);
}

  function completeWithdrawalForUser(
      address asset,
      address user,
      string calldata referralId
- ) external nonReentrant whenNotPaused onlyLRTOperator {
+ ) external nonReentrant onlyLRTOperator {
    _processWithdrawalCompletion(asset, user, referralId);
    emit AssetWithdrawalCompletedBy(msg.sender);
}
```

### Proof of Concept
1. User calls `initiateWithdrawal(asset, rsETHAmount, referralId)`. Their rsETH is transferred into `LRTWithdrawalManager` and a `WithdrawalRequest` is recorded with `withdrawalStartBlock = block.number`.
2. The operator calls `unlockQueue()` after the `withdrawalDelayBlocks` (default ~8 days) have passed, moving the request from locked to unlocked state.
3. Before the user calls `completeWithdrawal()`, the rsETH price drops sharply. `updateRSETHPrice()` is called (by anyone), triggering `LRTOracle._updateRsETHPrice()` which calls `withdrawalManager.pause()`.
4. The user attempts `completeWithdrawal()` — it reverts with `ContractPaused` due to `whenNotPaused`.
5. The user's rsETH remains locked in the contract. The underlying ETH/LST is inaccessible for the entire duration of the pause.
6. Only after an admin calls `unpause()` on `LRTWithdrawalManager` can the user complete their withdrawal. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L183-184)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
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

**File:** contracts/LRTWithdrawalManager.sol (L276-281)
```text
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
```

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```
