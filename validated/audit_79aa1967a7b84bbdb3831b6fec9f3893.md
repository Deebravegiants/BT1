### Title
Lack of Minimum Withdrawal Size Enables Unbounded Gas Consumption in `_unlockWithdrawalRequests` - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.initiateWithdrawal` enforces no effective minimum withdrawal size when `minRsEthAmountToWithdraw[asset]` is uninitialized (defaults to `0`). Any rsETH holder can flood the withdrawal queue with dust requests. The operator's `_unlockWithdrawalRequests` loop must iterate every queued request in order, making its gas cost proportional to the number of queued entries and enabling unbounded gas consumption or temporary freezing of legitimate withdrawals.

### Finding Description
`initiateWithdrawal` guards against zero-amount requests but relies on a per-asset mapping that defaults to `0`:

```solidity
// LRTWithdrawalManager.sol:162
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

Because `minRsEthAmountToWithdraw` is a `mapping(address => uint256)` with no initialization in `initialize()`, it defaults to `0` for every asset until an admin explicitly calls the setter. With a default of `0`, the condition `rsETHUnstaked < 0` is vacuously false for `uint256`, so any amount ≥ 1 wei passes.

Each accepted request is appended to the global FIFO queue and increments `nextUnusedNonce[asset]`:

```solidity
// LRTWithdrawalManager.sol:756-757
userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
```

The operator's unlock path calls `_unlockWithdrawalRequests`, which iterates every entry between `nextLockedNonce` and `firstExcludedIndex` in a `while` loop, performing multiple storage reads and writes per iteration:

```solidity
// LRTWithdrawalManager.sol:790-814
while (nextLockedNonce_ < firstExcludedIndex) {
    bytes32 requestId = getRequestId(asset, nextLockedNonce_);
    WithdrawalRequest storage request = withdrawalRequests[requestId];
    ...
    assetsCommitted[asset] -= request.expectedAssetAmount;
    request.expectedAssetAmount = payoutAmount;
    ...
    unlockedWithdrawalsCount[asset]++;
    unchecked { nextLockedNonce_++; }
}
```

An attacker who holds rsETH can submit thousands of 1-wei withdrawal requests. Because the queue is strictly FIFO, legitimate users' requests queued after the dust entries cannot be unlocked until all preceding dust entries are processed. If the operator passes a large `firstExcludedIndex` (e.g., `nextUnusedNonce[asset]`), the loop runs out of gas in a single transaction. Even with a bounded `firstExcludedIndex`, the operator must issue many transactions to drain the dust entries before reaching legitimate requests, temporarily freezing those users' funds.

### Impact Explanation
**Medium — Temporary freezing of funds / Unbounded gas consumption.**

Legitimate withdrawers whose requests are queued behind a flood of dust entries cannot complete their withdrawals until the operator processes every preceding entry. The operator's unlock transaction gas cost scales linearly with the number of queued entries; a sufficiently large flood causes the transaction to revert out-of-gas, stalling the entire withdrawal queue for the affected asset.

### Likelihood Explanation
Any rsETH holder (unprivileged, externally reachable) can call `initiateWithdrawal` with 1-wei amounts at will. The only cost to the attacker is gas and the temporary lock-up of a negligible rsETH balance (recovered after the withdrawal delay). The attack is cheap to execute and requires no special role or coordination.

### Recommendation
1. Require `minRsEthAmountToWithdraw[asset]` to be set to a non-zero value before the asset is usable for withdrawals, or initialize it to a sensible default (e.g., `1e15` wei) in `initialize()`.
2. Enforce the minimum strictly:
   ```solidity
   if (rsETHUnstaked == 0 || (minRsEthAmountToWithdraw[asset] > 0 && rsETHUnstaked < minRsEthAmountToWithdraw[asset])) {
       revert InvalidAmountToWithdraw();
   }
   ```
   Or simply ensure `minRsEthAmountToWithdraw[asset]` is always non-zero before the asset is supported.
3. Consider adding a cap on the number of pending withdrawal requests per user to further limit queue flooding.

### Proof of Concept
1. Admin deploys `LRTWithdrawalManager` and supports asset `ETH`. `minRsEthAmountToWithdraw[ETH]` is `0` (never set).
2. Attacker acquires 10,000 wei of rsETH.
3. Attacker calls `initiateWithdrawal(ETH, 1, "")` 10,000 times. Each call passes the `rsETHUnstaked == 0` check (1 ≠ 0) and the `< minRsEthAmountToWithdraw[ETH]` check (1 < 0 is false). Each call appends a new entry to the queue.
4. Legitimate user calls `initiateWithdrawal(ETH, 1 ether, "")`. Their request is at nonce 10,000.
5. Operator calls the unlock function with `firstExcludedIndex = nextUnusedNonce[ETH]` (10,001). The `_unlockWithdrawalRequests` while loop iterates all 10,001 entries, consuming ~3–4 storage ops × 10,001 iterations ≈ out-of-gas on mainnet.
6. Even if the operator batches in chunks, the legitimate user's withdrawal is delayed until all 10,000 dust entries are drained. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
