Audit Report

## Title
Uninitialized `minRsEthAmountToWithdraw` Enables Withdrawal Queue Spam, Causing Temporary Freezing of Funds - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary
`minRsEthAmountToWithdraw[asset]` defaults to `0` for all assets because `initialize` never sets it, reducing the guard in `initiateWithdrawal` to a zero-amount check only. An unprivileged attacker holding rsETH can flood the global nonce queue with dust requests; because `_unlockWithdrawalRequests` iterates sequentially with no ability to skip entries, legitimate users' requests queued behind the spam cannot be unlocked until the operator exhausts the spam entries, temporarily freezing those users' funds.

## Finding Description
**Root cause — uninitialized minimum:**
`initialize` (L90–98) never calls `setMinRsEthAmountToWithdraw`, so `minRsEthAmountToWithdraw[asset] == 0` for every asset at deployment. The guard in `initiateWithdrawal` (L162–164) is:

```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

With the mapping value at `0`, `rsETHUnstaked < 0` is always `false` for `uint256`, so any call with `rsETHUnstaked = 1` passes.

**Exploit path:**
1. Attacker approves the withdrawal manager and calls `initiateWithdrawal(asset, 1, "")` N times. Each call passes the guard, transfers 1 wei rsETH, and pushes a new entry into the sequential nonce queue via `_addUserWithdrawalRequest` (L756–757).
2. After the 8-day withdrawal delay passes, the operator calls `unlockQueue`. This invokes `_unlockWithdrawalRequests` (L770–816), which iterates from `nextLockedNonce[asset]` up to `firstExcludedIndex` in a `while` loop (L790–814). There is no mechanism to skip entries; the loop processes them strictly in order.
3. Each iteration performs multiple storage reads and writes (request lookup, `assetsCommitted` update, `request.expectedAssetAmount` write, `unlockedWithdrawalsCount` increment). With N large enough, a single `unlockQueue` call exceeds the block gas limit.
4. The operator can batch by passing a small `firstExcludedIndex`, but must still exhaust all N spam entries before `nextLockedNonce[asset]` advances past them. Until that happens, legitimate users whose requests have higher nonces cannot have their requests unlocked, and their rsETH remains locked in the contract.

**Why existing checks fail:**
- The `ExceedAmountToWithdraw` check (L170) compares `expectedAssetAmount` against available assets. For 1-wei rsETH requests the committed amount per request is negligible, so this check does not limit spam volume in practice.
- `setMinRsEthAmountToWithdraw` (L330–332) exists but is admin-only and is never invoked during initialization, leaving the default at `0`.

## Impact Explanation
**Medium — Temporary freezing of funds.** Legitimate users' rsETH is locked in the withdrawal manager contract. Their requests cannot be unlocked (and therefore `completeWithdrawal` will revert with `WithdrawalLocked`) until the operator processes all preceding spam entries. The operator can batch in small windows, but each batch requires a separate transaction, and with a sufficiently large spam queue the delay can span many blocks or days. This matches the allowed impact "Medium. Temporary freezing of funds."

## Likelihood Explanation
The attack requires only rsETH and L1 gas. The attacker recovers their rsETH after the 8-day delay, so the net cost is gas only. Approximately 1,000 spam transactions (each ~$1–2 on Ethereum mainnet at moderate gas prices) are sufficient to make a single `unlockQueue` call approach the block gas limit, given ~20,000–50,000 gas per loop iteration. No privileged access is required; `initiateWithdrawal` is a public, permissionless function. The attack is repeatable.

## Recommendation
1. Set a non-zero minimum for every supported asset inside `initialize`:
```solidity
function initialize(address lrtConfigAddr) external initializer {
    ...
    minRsEthAmountToWithdraw[LRTConstants.ETH_TOKEN] = 1e15; // 0.001 rsETH
}
```
2. Enforce a non-zero lower bound in the setter to prevent the admin from accidentally resetting it to `0`:
```solidity
function setMinRsEthAmountToWithdraw(address asset, uint256 min) external onlyLRTAdmin {
    if (min == 0) revert MinimumMustBeNonZero();
    minRsEthAmountToWithdraw[asset] = min;
    emit MinAmountToWithdrawUpdated(asset, min);
}
```

## Proof of Concept
```solidity
// Setup: attacker holds N * 1 wei rsETH
rsETH.approve(address(withdrawalManager), type(uint256).max);

// Step 1: flood the queue with N dust requests
for (uint256 i = 0; i < N; i++) {
    withdrawalManager.initiateWithdrawal(asset, 1, "spam");
}

// Step 2: wait withdrawalDelayBlocks (~57,600 blocks / 8 days)
vm.roll(block.number + withdrawalManager.withdrawalDelayBlocks());

// Step 3: operator attempts to unlock the queue
// With N large enough, this reverts out-of-gas
withdrawalManager.unlockQueue(
    asset,
    nextUnusedNonce,   // firstExcludedIndex covers all entries
    minAssetPrice,
    minRsEthPrice,
    maxAssetPrice,
    maxRsEthPrice
); // reverts: out of gas

// Legitimate users whose requests sit at nonces > spam entries
// cannot have their requests unlocked; completeWithdrawal reverts
// with WithdrawalLocked for all of them.
```

A Foundry fuzz test parameterizing `N` and measuring gas consumed per `unlockQueue` call will demonstrate the linear gas growth and the block-gas-limit crossing threshold.