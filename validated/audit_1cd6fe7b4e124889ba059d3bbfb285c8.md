Audit Report

## Title
Uninitialized `minRsEthAmountToWithdraw` allows dust-request flooding to temporarily freeze legitimate withdrawals — (File: `contracts/LRTWithdrawalManager.sol`)

## Summary

`minRsEthAmountToWithdraw[asset]` defaults to `0` for every asset and is never set in `initialize()`. The only effective guard in `initiateWithdrawal()` is `rsETHUnstaked == 0`, so any amount ≥ 1 wei of rsETH is accepted. Because `_unlockWithdrawalRequests()` processes the FIFO queue strictly in ascending nonce order with no ability to skip entries, an attacker who floods the queue with dust requests ahead of a legitimate user's request temporarily prevents that user from completing their withdrawal until the operator drains every preceding dust entry.

## Finding Description

**Root cause — uninitialized minimum:**

`LRTWithdrawalManager.sol` line 35 declares the mapping:
```solidity
mapping(address asset => uint256) public minRsEthAmountToWithdraw;
```
`initialize()` (lines 90–98) sets only `withdrawalDelayBlocks` and `lrtConfig`; `minRsEthAmountToWithdraw` is left at the Solidity default of `0` for every asset.

**Collapsed guard in `initiateWithdrawal()`:**

Lines 162–164:
```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```
When `minRsEthAmountToWithdraw[asset] == 0`, the second condition `rsETHUnstaked < 0` is always `false` for `uint256`, so the check reduces to `rsETHUnstaked == 0`. Any value ≥ 1 wei passes.

**FIFO queue cannot skip entries:**

`_unlockWithdrawalRequests()` (lines 790–815) iterates strictly from `nextLockedNonce_` upward:
```solidity
while (nextLockedNonce_ < firstExcludedIndex) {
    ...
    nextLockedNonce_++;
}
nextLockedNonce[asset] = nextLockedNonce_;
```
A request at nonce `N` cannot be unlocked until all requests at nonces `0 … N-1` have been processed. There is no skip or cancel mechanism.

**`setMinRsEthAmountToWithdraw` accepts zero:**

Lines 330–333 contain no zero-value guard, so even if an admin sets a minimum it can be silently reset to `0`.

**Cheap rsETH acquisition:**

`LRTDepositPool._beforeDeposit()` (line 657) applies the same collapsed guard: `depositAmount == 0 || depositAmount < minAmountToDeposit`. Since `minAmountToDeposit` also defaults to `0`, depositing 1 wei of ETH yields 1 wei of rsETH, giving the attacker an arbitrarily cheap supply of dust amounts.

**Exploit path:**
1. Attacker deposits 1 wei ETH per iteration → receives 1 wei rsETH each time.
2. Attacker calls `initiateWithdrawal(ETH_TOKEN, 1, "")` N times → nonces 0 … N-1 filled with dust entries.
3. Victim calls `initiateWithdrawal(ETH_TOKEN, 1e18, "")` → queued at nonce N.
4. Operator calls `unlockQueue(…)`. The loop must iterate through all N dust entries before reaching nonce N.
5. `completeWithdrawal()` for the victim reverts with `WithdrawalLocked` (line 707) until `nextLockedNonce[asset] > N`, which requires the operator to drain all N dust entries across many gas-bounded `unlockQueue` calls.

## Impact Explanation

**Temporary freezing of funds (Medium).** Legitimate users whose withdrawal requests are queued after the attacker's dust entries cannot have their requests unlocked — and therefore cannot call `completeWithdrawal()` — until the operator processes every preceding dust entry. This extends the effective withdrawal delay beyond the already-mandatory `withdrawalDelayBlocks` (~8 days) by however long it takes the operator to drain the queue.

**Unbounded gas consumption (Medium).** The operator must call `unlockQueue()` repeatedly; total operator gas cost scales linearly with the number of dust entries the attacker creates.

## Likelihood Explanation

Any address holding rsETH can execute this attack. rsETH is freely obtainable via `LRTDepositPool.depositETH()` with no minimum deposit enforced. The attacker's only cost is gas per dust request and a temporary lock-up of their own rsETH (which they eventually recover). The cost asymmetry strongly favours the attacker: N deposit + N `initiateWithdrawal` transactions for the attacker versus N `unlockQueue` iterations for the operator plus indefinite blocking of all legitimate users queued behind the dust entries.

## Recommendation

1. **Enforce a non-zero minimum in `initialize()`**: Set a sensible default for `minRsEthAmountToWithdraw` for each supported asset during initialisation (e.g., equivalent to ~0.001 ETH worth of rsETH).
2. **Guard `setMinRsEthAmountToWithdraw` against zero**: Add `if (minRsEthAmountToWithdraw_ == 0) revert InvalidMinAmount();` analogous to guards present elsewhere in the codebase.
3. **Guard `setMinAmountToDeposit` against zero** in `LRTDepositPool` for the same reason, to prevent cheap rsETH acquisition in arbitrarily small increments.

## Proof of Concept

```solidity
// Precondition: minRsEthAmountToWithdraw[ETH_TOKEN] == 0 (default, never set in initialize())
// Precondition: minAmountToDeposit == 0 (default, never set in initialize())

// Step 1: Attacker acquires dust rsETH
// depositETH{value: N wei}() → N wei rsETH (1:1 at par, integer division)
// _beforeDeposit guard: depositAmount == 0 → false; depositAmount < 0 → false → passes

// Step 2: Attacker floods queue
// for i in range(1_000_000):
//     initiateWithdrawal(ETH_TOKEN, 1, "") → nonce i
// Guard: 1 == 0 → false; 1 < 0 → false → passes each time

// Step 3: Victim queues legitimate withdrawal
// initiateWithdrawal(ETH_TOKEN, 1e18, "") → nonce 1_000_000

// Step 4: Operator attempts to unlock
// unlockQueue(ETH_TOKEN, 1_000_001, ...)
// _unlockWithdrawalRequests loops from nextLockedNonce=0 to 1_000_001
// Must process all 1,000,000 dust entries (each consuming ~1 wei of assets)
// before nextLockedNonce reaches 1_000_000

// Step 5: Victim's completeWithdrawal() reverts
// usersFirstWithdrawalRequestNonce (1_000_000) >= nextLockedNonce[asset] → WithdrawalLocked
// Victim is frozen until operator drains all dust entries across many batched unlockQueue calls
```

**Foundry fuzz test sketch:**
```solidity
function testFuzz_dustFloodFreezesVictim(uint256 dustCount) public {
    dustCount = bound(dustCount, 100, 10_000);
    // fund attacker with dustCount wei of rsETH
    // attacker calls initiateWithdrawal(ETH_TOKEN, 1, "") dustCount times
    // victim calls initiateWithdrawal(ETH_TOKEN, 1e18, "")
    // warp past withdrawalDelayBlocks
    // operator calls unlockQueue with firstExcludedIndex = dustCount (not dustCount+1)
    // assert: victim's completeWithdrawal() reverts WithdrawalLocked
    // operator calls unlockQueue with firstExcludedIndex = dustCount+1
    // assert: victim's completeWithdrawal() succeeds
}
```