Audit Report

## Title
Unbounded Withdrawal Queue Flooding via Dust `initiateWithdrawal` Calls Causes Unbounded Gas Consumption in `_unlockWithdrawalRequests` - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTWithdrawalManager.initiateWithdrawal` accepts any non-zero rsETH amount when `minRsEthAmountToWithdraw[asset]` is at its default value of zero, allowing any unprivileged user to flood the per-asset withdrawal queue with arbitrarily many dust entries. The internal `_unlockWithdrawalRequests` function processes the queue in strict FIFO order with no skip mechanism, causing gas consumption to scale linearly with queue depth and temporarily preventing legitimate withdrawal requests queued behind the dust entries from being unlocked within a single block.

## Finding Description
`minRsEthAmountToWithdraw` is declared as `mapping(address asset => uint256) public minRsEthAmountToWithdraw` at line 35 of `LRTWithdrawalManager.sol`, whose Solidity default for every key is `0`. The guard in `initiateWithdrawal` (line 162) is:

```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

When `minRsEthAmountToWithdraw[asset] == 0`, the sub-expression `rsETHUnstaked < 0` is vacuously false for `uint256`, so any amount `> 0` passes. Each accepted call pushes a new entry into the global queue via `_addUserWithdrawalRequest` (lines 744–757) and increments `nextUnusedNonce[asset]` without bound.

The operator-facing unlock path calls `_unlockWithdrawalRequests` (lines 770–816), which iterates from `nextLockedNonce[asset]` to `firstExcludedIndex` in a `while` loop. Each iteration performs at minimum one cold `SLOAD` for `withdrawalRequests[requestId]`, one `SSTORE` for `assetsCommitted[asset]`, one `SSTORE` for `request.expectedAssetAmount`, and one `SSTORE` for `unlockedWithdrawalsCount[asset]`. The operator controls `firstExcludedIndex` but cannot skip over unprocessed entries — `nextLockedNonce[asset]` advances only sequentially, so dust entries at the front of the queue must be individually processed before any legitimate request queued later can be reached.

`minAmountToDeposit` in `LRTDepositPool` (line 657) also defaults to `0`, meaning depositing 1 wei of ETH is sufficient to obtain a non-zero rsETH balance, making the cost of each spam entry only gas.

## Impact Explanation
**Medium — Unbounded gas consumption; temporary freezing of funds.**

At roughly 15,000–20,000 gas per loop iteration (cold SLOAD + multiple SSTOREs), the Ethereum block gas limit (~30 M gas) allows only ~1,500–2,000 entries to be processed per `unlockQueue` call. An attacker who queues more dust entries than this threshold ahead of a legitimate withdrawal request prevents that request from being unlocked in any single transaction until the dust is cleared across many operator calls, temporarily freezing those funds. Both "Medium. Unbounded gas consumption" and "Medium. Temporary freezing of funds" from the allowed impact scope are concretely satisfied.

## Likelihood Explanation
**Medium.** The attack requires no special privileges — `initiateWithdrawal` is a public function callable by any address holding a non-zero rsETH balance. With both `minAmountToDeposit` and `minRsEthAmountToWithdraw` at their zero defaults, the only cost to the attacker is gas per spam call; the rsETH principal is returned when each dust request is eventually processed. The attack is repeatable across multiple addresses and assets, and no protocol-level barrier prevents it on a freshly deployed or uninitialized instance.

## Recommendation
1. **Enforce a non-zero minimum withdrawal amount at asset registration.** Set `minRsEthAmountToWithdraw[asset]` to a meaningful floor (e.g., `0.001 ether` worth of rsETH) for every supported asset when the asset is added, rather than relying on a post-deployment admin call to `updateMinRsEthAmountToWithdraw`.
2. **Enforce a non-zero minimum deposit amount.** Set `minAmountToDeposit` to a meaningful floor at initialization to raise the cost of obtaining dust rsETH.
3. **Cap pending withdrawal requests per user per asset.** Analogous to `KernelDepositPool.maxNumberOfWithdrawalsPerUser`, add a per-user cap on the `userAssociatedNonces` deque length to limit how many requests a single address can queue simultaneously.

## Proof of Concept
```solidity
// Preconditions (defaults, no admin action needed):
//   minRsEthAmountToWithdraw[ETH_TOKEN] == 0  (mapping default)
//   minAmountToDeposit == 0                    (mapping default)

// Step 1: Attacker deposits 1 wei ETH → receives tiny rsETH
lrtDepositPool.depositETH{value: 1}(0, "");

// Step 2: Attacker approves withdrawal manager
rsETH.approve(address(withdrawalManager), type(uint256).max);

// Step 3: Repeat N times across multiple addresses if needed
for (uint i = 0; i < N; i++) {
    withdrawalManager.initiateWithdrawal(ETH_TOKEN, 1, "spam");
}
// nextUnusedNonce[ETH_TOKEN] == N
// Operator's unlockQueue must iterate all N dust entries before
// reaching any legitimate request queued after the spam.
// Gas cost of unlockQueue scales O(N); at N > ~2000, exceeds block gas limit.
```

A Foundry fork test can confirm this by: (1) deploying with default parameters, (2) minting dust rsETH via `depositETH`, (3) calling `initiateWithdrawal` in a loop to fill the queue, (4) advancing blocks past `withdrawalDelayBlocks`, and (5) measuring gas consumed by `unlockQueue` as N increases, verifying it exceeds 30 M gas at a feasible N.