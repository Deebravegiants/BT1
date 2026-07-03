Audit Report

## Title
Automatic Price-Drop Circuit Breaker Pauses `LRTWithdrawalManager`, Temporarily Freezing In-Queue User Funds - (File: contracts/LRTWithdrawalManager.sol)

## Summary
`LRTWithdrawalManager` guards `completeWithdrawal()` and `completeWithdrawalForUser()` with `whenNotPaused`. The pause can be triggered automatically by any public caller of `LRTOracle.updateRSETHPrice()` when the rsETH price drops beyond `pricePercentageLimit`. Users who have already transferred rsETH into the contract via `initiateWithdrawal()` cannot retrieve their underlying ETH/LSTs for the entire duration of the pause, constituting a temporary freeze of user funds.

## Finding Description
`initiateWithdrawal()` immediately pulls rsETH from the user into the contract:

```solidity
// LRTWithdrawalManager.sol L166
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

Once rsETH is held by the contract, the user must wait for `unlockQueue()` and then call `completeWithdrawal()` to receive their asset. Both completion paths are gated:

```solidity
// L183
function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {

// L199
) external nonReentrant whenNotPaused onlyLRTOperator {
```

`unlockQueue()` is also gated by `whenNotPaused` (L279), blocking operator processing as well.

The pause is triggered automatically — not solely by an admin — inside `LRTOracle._updateRsETHPrice()`:

```solidity
// LRTOracle.sol L277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

`updateRSETHPrice()` is a public, permissionless function:

```solidity
// LRTOracle.sol L87
function updateRSETHPrice() public whenNotPaused {
```

Any external caller can invoke it. If the computed `newRsETHPrice` has dropped more than `pricePercentageLimit` below `highestRsethPrice`, the function automatically calls `withdrawalManager.pause()`. This is a realistic, non-privileged trigger path.

## Impact Explanation
Temporary freezing of funds (Medium). Users who have already submitted `initiateWithdrawal()` — transferring their rsETH into `LRTWithdrawalManager` — cannot call `completeWithdrawal()` to receive their ETH/LST while the contract is paused. Their rsETH is held in the contract and the underlying assets are inaccessible for an indefinite period until an admin calls `unpause()`. The rsETH is not permanently lost, but users are denied access to their assets during the pause. This matches the allowed impact: **Medium — Temporary freezing of funds**.

## Likelihood Explanation
Medium. `updateRSETHPrice()` is callable by any unprivileged external account. The price-drop condition (`newRsETHPrice < highestRsethPrice` by more than `pricePercentageLimit`) is plausible during market stress — precisely when users most urgently need to complete withdrawals. No admin collusion or special privilege is required; the trigger is purely market-condition-dependent and reachable by any EOA or contract.

## Recommendation
Remove `whenNotPaused` from `completeWithdrawal()` and `completeWithdrawalForUser()` so users with already-queued, already-unlocked withdrawal requests can always claim their assets. `initiateWithdrawal()` and `instantWithdrawal()` may reasonably remain paused to prevent new commitments during emergencies. `unlockQueue()` should similarly remain callable while paused so operator processing is not blocked.

```diff
- function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
+ function completeWithdrawal(address asset, string calldata referralId) external nonReentrant {

  function completeWithdrawalForUser(
      address asset,
      address user,
      string calldata referralId
- ) external nonReentrant whenNotPaused onlyLRTOperator {
+ ) external nonReentrant onlyLRTOperator {
```

## Proof of Concept
1. User calls `initiateWithdrawal(asset, rsETHAmount, referralId)`. rsETH is transferred into `LRTWithdrawalManager` at L166 and a `WithdrawalRequest` is recorded.
2. After `withdrawalDelayBlocks` (~8 days), the operator calls `unlockQueue()`, moving the request to unlocked state.
3. The rsETH price drops sharply. Any external account calls `LRTOracle.updateRSETHPrice()`. Inside `_updateRsETHPrice()`, `isPriceDecreaseOffLimit` evaluates to `true`, and `withdrawalManager.pause()` is called at L279.
4. User calls `completeWithdrawal(asset, referralId)` — it reverts with `ContractPaused` due to `whenNotPaused` at L183.
5. User's rsETH remains locked in the contract; the underlying ETH/LST is inaccessible for the entire duration of the pause.
6. Only after an admin calls `unpause()` on `LRTWithdrawalManager` (L352) can the user complete their withdrawal.

**Foundry test sketch:**
```solidity
// 1. Setup: user initiates withdrawal, operator unlocks queue
// 2. Manipulate oracle state so newRsETHPrice < highestRsethPrice * (1 - pricePercentageLimit)
// 3. Call lrtOracle.updateRSETHPrice() from an unprivileged address
// 4. Assert withdrawalManager.paused() == true
// 5. vm.expectRevert(); withdrawalManager.completeWithdrawal(asset, "");
// 6. Assert user's rsETH balance in contract is unchanged
```