### Title
Block-Based Withdrawal Delay Hardcodes 12-Second Block Time Assumption, Causing Premature or Delayed Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager` enforces its withdrawal delay entirely in `block.number` units, with both the default value and the enforced upper bound computed by dividing a day-count by a hardcoded 12-second block time. If Ethereum's average block time deviates from 12 seconds, the real-time delay diverges proportionally from the intended 8-day window, either allowing withdrawals to complete before EigenLayer has returned the underlying assets (temporary fund freeze / insolvency risk) or locking users out longer than promised.

### Finding Description
`withdrawalDelayBlocks` is initialised as `8 days / 12 seconds` (57,600 blocks) and the setter caps it at `16 days / 12 seconds` (115,200 blocks), both silently embedding the assumption that one block equals exactly 12 seconds. [1](#0-0) [2](#0-1) 

At request creation, the current `block.number` is stored as `withdrawalStartBlock`: [3](#0-2) 

Both the operator-facing `_unlockWithdrawalRequests` and the user-facing `_processWithdrawalCompletion` gate progress on a pure block-number comparison: [4](#0-3) [5](#0-4) 

There is no `block.timestamp`-based fallback. The entire delay mechanism is block-count arithmetic.

### Impact Explanation
The 8-day delay is calibrated to cover EigenLayer's withdrawal queue period. If the average block time drops below 12 seconds (e.g., a future Ethereum protocol change, or reuse of this contract on a faster EVM-compatible chain), the block count `57,600` corresponds to fewer than 8 real-time days. Operators can then call `unlockQueue` and users can call `completeWithdrawal` before EigenLayer has actually returned the underlying LSTs/ETH to `LRTUnstakingVault`. At that point `unstakingVault.redeem` inside `unlockQueue` draws on assets that have not yet arrived, and subsequent `completeWithdrawal` calls revert for lack of balance — temporarily freezing user funds. Conversely, if block times increase, users are locked out longer than the protocol promises, also constituting a temporary freeze. Errors are cumulative across every in-flight withdrawal request and cannot be corrected retroactively for already-queued requests.

**Impact rating: Medium — Temporary freezing of funds.**

### Likelihood Explanation
Ethereum mainnet block times have been stable near 12 seconds post-Merge, but the hardcoded assumption creates a latent risk that activates automatically with any protocol-level change to slot timing or if the contract is deployed to any EVM chain with a different block cadence. No attacker action is required; the divergence occurs passively. Any depositor who has initiated a withdrawal is affected.

### Recommendation
Replace the block-count delay with a timestamp-based delay. Store `block.timestamp` at request creation instead of `block.number`, and compare against `block.timestamp` at completion:

```solidity
// Storage
uint256 public withdrawalDelaySeconds;   // replaces withdrawalDelayBlocks

// initialize
withdrawalDelaySeconds = 8 days;

// setter upper bound
if (withdrawalDelaySeconds_ > 16 days) revert ExceedWithdrawalDelay();

// request creation
withdrawalRequests[requestId] = WithdrawalRequest({
    ...,
    withdrawalStartTime: block.timestamp   // replaces withdrawalStartBlock
});

// enforcement (both _unlockWithdrawalRequests and _processWithdrawalCompletion)
if (block.timestamp < request.withdrawalStartTime + withdrawalDelaySeconds)
    revert/break;
```

`block.timestamp` manipulation by validators is bounded to a few seconds per block and is non-cumulative, making it far more robust for multi-day delay enforcement than block counting.

### Proof of Concept
1. Assume Ethereum reduces its target slot time to 8 seconds (a plausible future change).
2. `withdrawalDelayBlocks` remains `57,600` (set at initialisation; no automatic recalculation).
3. A user calls `initiateWithdrawal`; `withdrawalStartBlock = N`.
4. After `57,600 * 8 s = 5.33 days` of real time, `block.number == N + 57,600`.
5. The operator calls `unlockQueue`: the block-number check passes, rsETH is burned, and `unstakingVault.redeem` is called — but EigenLayer's 7-day withdrawal queue has not yet completed, so the vault has no ETH/LST to disburse.
6. `completeWithdrawal` reverts for every affected user until EigenLayer eventually settles (~1.67 days later), freezing their funds for that period.
7. The error compounds for every withdrawal queued during the period of divergent block times; no retroactive fix is possible for already-unlocked requests. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L340-340)
```text
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
