### Title
Retroactive Extension of `withdrawalDelayBlocks` Temporarily Freezes In-Flight Withdrawal Funds - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager` reads the global `withdrawalDelayBlocks` at withdrawal-completion time rather than storing it at initiation time. When the manager legitimately increases `withdrawalDelayBlocks` after users have already transferred their rsETH into the contract via `initiateWithdrawal`, those users' funds are retroactively locked beyond the delay they accepted at deposit time.

### Finding Description
When a user calls `initiateWithdrawal`, their rsETH is immediately transferred into `LRTWithdrawalManager` and a `WithdrawalRequest` is stored with only `withdrawalStartBlock`: [1](#0-0) 

The `withdrawalDelayBlocks` value is **not** snapshotted into the request. Both the operator-triggered `_unlockWithdrawalRequests` path and the user-triggered `_processWithdrawalCompletion` path read the current global value at execution time: [2](#0-1) [3](#0-2) 

The manager can increase `withdrawalDelayBlocks` up to the 16-day cap at any time: [4](#0-3) 

Because both the unlock gate and the completion gate use the live global value, any increase retroactively extends the lock on **all** pending withdrawal requests whose rsETH is already held by the contract.

### Impact Explanation
**Medium — Temporary freezing of funds.**

A user who initiated a withdrawal expecting an 8-day delay (the initialization default) will find their rsETH locked in the contract for up to 16 days if the manager raises the delay after initiation. The user cannot cancel the withdrawal, cannot transfer the rsETH (it is held by the contract), and cannot complete the withdrawal until the new delay elapses. The maximum additional lock is bounded by the 16-day cap, so the freeze is temporary, not permanent. [5](#0-4) 

### Likelihood Explanation
**Medium.** Increasing `withdrawalDelayBlocks` is a routine, legitimate governance action — for example, during a security incident, a market stress event, or an EigenLayer upgrade requiring a longer settlement window. No malicious intent is required; the side-effect on existing in-flight withdrawals is a design fragility. The manager role is a single address with no timelock on this setter, so the change can take effect immediately. [6](#0-5) 

### Recommendation
Snapshot `withdrawalDelayBlocks` into each `WithdrawalRequest` at initiation time and use the stored value in both `_unlockWithdrawalRequests` and `_processWithdrawalCompletion`. This ensures users are bound only by the delay that was in effect when they committed their rsETH, consistent with the per-withdrawal tracking already used for `withdrawalStartBlock`.

Alternatively, add a governance timelock on `setWithdrawalDelayBlocks` so that any increase only applies to withdrawals initiated after the timelock expires, giving existing users time to complete their withdrawals under the old delay.

### Proof of Concept

1. `withdrawalDelayBlocks` is initialized to `8 days / 12 seconds` (~57,600 blocks).
2. Alice calls `initiateWithdrawal(ETH, 10e18, "")`. Her rsETH is transferred to the contract. Her `WithdrawalRequest.withdrawalStartBlock = B`.
3. At block `B + 57,600` Alice expects to call `completeWithdrawal`.
4. Before block `B + 57,600`, the manager calls `setWithdrawalDelayBlocks(16 days / 12 seconds)` (~115,200 blocks) — a legitimate security response.
5. Alice calls `completeWithdrawal` at block `B + 57,600`. The check `block.number < request.withdrawalStartBlock + withdrawalDelayBlocks` evaluates as `B + 57,600 < B + 115,200` → **reverts with `WithdrawalDelayNotPassed`**.
6. Alice's rsETH remains locked in the contract for an additional ~8 days beyond what she accepted, with no recourse. [3](#0-2) [2](#0-1)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L91-97)
```text
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();
        withdrawalDelayBlocks = 8 days / 12 seconds;

        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
```

**File:** contracts/LRTWithdrawalManager.sol (L336-344)
```text
    /// @dev only callable by LRT manager
    /// @param withdrawalDelayBlocks_ The amount of blocks to wait till to complete a withdraw
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L714-716)
```text
        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

```

**File:** contracts/LRTWithdrawalManager.sol (L750-757)
```text
        // Create and store the new withdrawal request.
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });

        // Map the user to the newly created request index and increment the nonce for future requests.
        userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
        nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
```

**File:** contracts/LRTWithdrawalManager.sol (L794-796)
```text
            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

```
