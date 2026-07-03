### Title
`block.number`-Based Withdrawal Delay Hardcodes 12-Second Ethereum Block Time Assumption — (`File: contracts/LRTWithdrawalManager.sol`)

### Summary
`LRTWithdrawalManager` enforces its withdrawal delay entirely in block counts, with the initial value and the admin-settable upper bound both derived by dividing a wall-clock duration by the Ethereum-specific constant of 12 seconds per block. On any chain where blocks are produced at a different cadence the real-time delay diverges from the intended 8-day window, either allowing users to complete withdrawals far earlier than intended or locking their funds for far longer.

### Finding Description
`LRTWithdrawalManager.initialize()` seeds `withdrawalDelayBlocks` with the expression `8 days / 12 seconds`, which evaluates to 57,600 blocks under the assumption that every block takes exactly 12 seconds. [1](#0-0) 

The manager-callable setter `setWithdrawalDelayBlocks` enforces an upper bound using the same assumption: [2](#0-1) 

Both the unlock gate in `_unlockWithdrawalRequests` and the completion gate in `_processWithdrawalCompletion` compare `block.number` against `withdrawalStartBlock + withdrawalDelayBlocks`: [3](#0-2) [4](#0-3) 

The withdrawal start block is stamped at request time: [5](#0-4) 

### Impact Explanation
On a chain producing blocks every 2 seconds (e.g., many OP-stack or zkSync deployments), 57,600 blocks elapse in roughly 1.3 days instead of 8 days. A user who initiates a withdrawal can call `completeWithdrawal` after only ~1.3 days, bypassing the intended 8-day security window. Conversely, on a chain with 30-second blocks the same 57,600 blocks take ~20 days, locking user funds for more than twice the intended period — a temporary freeze of user funds. The upper-bound guard of `16 days / 12 seconds` is equally miscalibrated, so the manager cannot correct the problem by raising the delay on a fast-block chain.

**Impact: Medium — Temporary freezing of funds (slow-block chain) / premature release of withdrawal delay (fast-block chain).**

### Likelihood Explanation
The pool contracts (`RSETHPoolV2`, `RSETHPoolV3`) are already deployed on multiple L2 chains. The withdrawal manager is the natural companion contract for any such deployment. The hardcoded constant is baked into `initialize()` and requires no attacker action — it activates automatically the moment the contract is deployed on a non-Ethereum chain. Any depositor who initiates a withdrawal is directly affected.

### Recommendation
Replace the block-count delay with a timestamp-based delay. Store `withdrawalStartTimestamp` (using `block.timestamp`) in the `WithdrawalRequest` struct and compare against `block.timestamp` at completion time, mirroring the approach already used in `KernelDepositPool` for its own withdrawal delay: [6](#0-5) [7](#0-6) 

If block-count delays must be retained for Ethereum mainnet, document the 12-second assumption explicitly and provide a chain-specific initializer parameter rather than a hardcoded constant.

### Proof of Concept
1. Deploy `LRTWithdrawalManager` on a chain with 2-second block times.
2. `initialize()` sets `withdrawalDelayBlocks = 8 days / 12 seconds = 57,600`.
3. User calls `initiateWithdrawal(asset, amount)`. `withdrawalStartBlock = block.number` is recorded.
4. After 57,600 blocks (≈ 1.33 days on a 2-second chain), the operator calls `unlockQueue` — the check `block.number < request.withdrawalStartBlock + withdrawalDelayBlocks` passes.
5. User calls `completeWithdrawal` and receives funds after only ~1.33 days, well before the intended 8-day security window.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L338-341)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

```

**File:** contracts/LRTWithdrawalManager.sol (L715-715)
```text
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

**File:** contracts/LRTWithdrawalManager.sol (L751-753)
```text
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });
```

**File:** contracts/LRTWithdrawalManager.sol (L795-795)
```text
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L330-330)
```text
        uint256 unlockTime = block.timestamp + withdrawalDelay;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L355-357)
```text
        if (block.timestamp < withdrawal.unlockTime) {
            revert WithdrawalNotReady();
        }
```
