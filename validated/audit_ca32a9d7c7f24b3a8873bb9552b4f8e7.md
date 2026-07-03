### Title
Manager Can Retroactively Extend Withdrawal Delay After Users Submit Requests, Temporarily Freezing Funds - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.setWithdrawalDelayBlocks` allows the `LRT_MANAGER` role to increase the global `withdrawalDelayBlocks` at any time — including after users have already submitted withdrawal requests and transferred their rsETH into the contract. Because both the unlock gate and the completion gate read the **current** global `withdrawalDelayBlocks` rather than the value snapshotted at submission time, a manager-triggered increase retroactively extends the wait for every in-flight request, temporarily freezing user funds.

---

### Finding Description

When a user calls `initiateWithdrawal`, their rsETH is immediately transferred into `LRTWithdrawalManager` and a `WithdrawalRequest` is stored with `withdrawalStartBlock = block.number`. [1](#0-0) 

The request records only `withdrawalStartBlock`; it does **not** snapshot the delay that was in effect at submission time. [2](#0-1) 

Both downstream enforcement points read the live global `withdrawalDelayBlocks`:

**`_processWithdrawalCompletion` (user-facing completion):** [3](#0-2) 

**`_unlockWithdrawalRequests` (operator-triggered unlock):** [4](#0-3) 

The manager setter has no restriction on when it may be called and accepts any value up to `16 days / 12 seconds`: [5](#0-4) 

The contract is initialized with an 8-day default: [6](#0-5) 

A manager can therefore call `setWithdrawalDelayBlocks(16 days / 12 seconds)` at any moment — before or after users submit — and every pending request that has not yet passed the new threshold is immediately re-locked for the extended duration.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

Users' rsETH is held by the contract from the moment `initiateWithdrawal` is called. If the manager raises `withdrawalDelayBlocks` from the 8-day default to the 16-day maximum after submission, every in-flight request is frozen for up to an additional 8 days beyond what the user expected when they submitted. The manager can repeat this pattern for each new cohort of requests, keeping funds locked at the ceiling for the full duration of each request's life. Funds are not permanently lost, but users cannot exit on the timeline they relied upon.

---

### Likelihood Explanation

**Low-Medium.** The `LRT_MANAGER` role is a protocol-controlled privileged key, not an unprivileged caller. However, the vulnerability requires no external compromise — it is exercisable by the role acting within its on-chain permissions, exactly as in the reference report where `OPEN_ROLE` (held by the Aragon Network DAO) could extend the presale period. The risk is elevated because the setter has no guard against retroactive application and no on-chain notice period.

---

### Recommendation

Snapshot `withdrawalDelayBlocks` into each `WithdrawalRequest` at submission time and use the per-request snapshot for all delay checks, rather than the live global value. Alternatively, restrict `setWithdrawalDelayBlocks` so that it only affects requests submitted **after** the change (e.g., by recording the block at which the change takes effect and comparing against `withdrawalStartBlock`).

---

### Proof of Concept

1. `withdrawalDelayBlocks` is initialized to `8 days / 12 seconds` (57,600 blocks).
2. Alice calls `initiateWithdrawal(asset, rsETHAmount, ...)` at block **N**. Her rsETH is transferred to the contract. She expects to complete after ~8 days (block N + 57,600).
3. The `LRT_MANAGER` calls `setWithdrawalDelayBlocks(16 days / 12 seconds)` (115,200 blocks) — permitted with no preconditions.
4. At block N + 57,600, Alice calls `completeWithdrawal`. The check `block.number < request.withdrawalStartBlock + withdrawalDelayBlocks` evaluates to `N+57600 < N+115200` → **true** → reverts with `WithdrawalDelayNotPassed`.
5. Alice must wait until block N + 115,200 (~16 days from submission) to recover her assets — 8 days longer than the delay in effect when she submitted.
6. The manager may repeat step 3 for every new cohort of requests, keeping each batch locked at the 16-day ceiling for the full duration of their life. [5](#0-4) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L338-344)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
    }
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
