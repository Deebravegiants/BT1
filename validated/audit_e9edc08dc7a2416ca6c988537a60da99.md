Let me examine the critical functions more closely to trace the exact execution flow.

### Title
Reverting-receive contract permanently blocks `sweepRemainingAssets` for ETH via stuck `unlockedWithdrawalsCount` — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

A user whose address is a contract with a reverting `receive()` function can permanently freeze `unlockedWithdrawalsCount[ETH]` at a non-zero value. Because `_transferAsset` for ETH reverts the entire `_processWithdrawalCompletion` call (including the counter decrement), the counter can never reach zero, causing every subsequent `sweepRemainingAssets(ETH)` call to revert with `PendingWithdrawalsExist()`. There is no admin escape hatch to cancel the stuck request or manually correct the counter.

---

### Finding Description

**Root cause — ordering of state mutation and ETH transfer in `_processWithdrawalCompletion`:**

`unlockedWithdrawalsCount[asset]--` is executed at line 717, *before* `_transferAsset` at line 734. [1](#0-0) 

`_transferAsset` for ETH uses a low-level call and reverts the whole transaction on failure: [2](#0-1) 

Because Solidity reverts all state changes on a revert, the decrement at line 717 is rolled back. The counter stays at its pre-call value indefinitely.

**Counter is incremented during `unlockQueue`:**

`_unlockWithdrawalRequests` increments `unlockedWithdrawalsCount[asset]` for every request it processes: [3](#0-2) 

**`sweepRemainingAssets` is gated on the counter:**

```solidity
if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
``` [4](#0-3) 

`hasUnlockedWithdrawals` simply checks `unlockedWithdrawalsCount[asset] > 0`: [5](#0-4) 

**No escape hatch exists.** There is no admin function to cancel a withdrawal request, force-decrement the counter, or route the ETH to an alternative address. `completeWithdrawalForUser` (the operator-callable variant) also routes through `_processWithdrawalCompletion` and fails identically. The `initialize2`/`initialize3` reinitializers are one-shot and already consumed on mainnet. [6](#0-5) 

---

### Impact Explanation

`sweepRemainingAssets(ETH)` is permanently blocked for the affected asset. Any ETH balance that accumulates in the contract beyond committed withdrawals — including rounding residuals from Aave principal withdrawals, direct ETH sends via `receive()`, or any future surplus — cannot be recovered to the treasury. This constitutes **permanent freezing of unclaimed yield** (Medium impact per scope).

---

### Likelihood Explanation

The attacker only needs:
1. A small amount of rsETH (obtainable by depositing ETH or any supported LST).
2. A contract with a reverting `receive()` (trivial to deploy).

No privileged role is required from the attacker. The operator's `unlockQueue` call is a normal operational action that will happen regardless. The attack is cheap, deterministic, and requires no front-running.

---

### Recommendation

**Option A (preferred):** Decouple the ETH transfer from the counter decrement by using a pull-payment pattern. Store the owed ETH amount in a per-user claimable balance mapping instead of pushing ETH in `_processWithdrawalCompletion`. Decrement `unlockedWithdrawalsCount` and delete the request atomically, then let the user pull their ETH separately.

**Option B:** Add an admin function that can forcibly cancel a stuck unlocked withdrawal request (refunding rsETH or redirecting ETH to a recovery address) and correctly decrements `unlockedWithdrawalsCount`.

**Option C (minimal):** Move `unlockedWithdrawalsCount[asset]--` to *after* the successful `_transferAsset` call, and wrap the transfer in a try/catch that marks the request as "failed" rather than reverting the whole transaction.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// 1. Deploy this contract and fund it with rsETH
contract RevertingReceiver {
    receive() external payable { revert("no ETH"); }

    function attack(
        address withdrawalManager,
        address rsETH,
        uint256 rsETHAmount
    ) external {
        // Approve and initiate withdrawal for ETH
        IERC20(rsETH).approve(withdrawalManager, rsETHAmount);
        ILRTWithdrawalManager(withdrawalManager)
            .initiateWithdrawal(ETH_TOKEN, rsETHAmount, "");
    }
}

// 2. Operator calls unlockQueue(ETH_TOKEN, ...) — unlockedWithdrawalsCount[ETH] becomes 1

// 3. Any call to completeWithdrawal / completeWithdrawalForUser reverts with EthTransferFailed
//    because payable(RevertingReceiver).call{value: amount}("") returns false.
//    The decrement at line 717 is rolled back. Counter stays at 1.

// 4. Assert:
//    hasUnlockedWithdrawals(ETH_TOKEN) == true  (forever)
//    sweepRemainingAssets(ETH_TOKEN) reverts with PendingWithdrawalsExist()  (forever)
```

The counter `unlockedWithdrawalsCount[ETH]` is permanently non-zero, and `sweepRemainingAssets` is permanently blocked for ETH. [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L58-58)
```text
    mapping(address asset => uint256) public unlockedWithdrawalsCount;
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

**File:** contracts/LRTWithdrawalManager.sol (L403-403)
```text
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```

**File:** contracts/LRTWithdrawalManager.sol (L629-631)
```text
    function hasUnlockedWithdrawals(address asset) public view returns (bool hasUnlocked) {
        return unlockedWithdrawalsCount[asset] > 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L717-717)
```text
        unlockedWithdrawalsCount[asset]--;
```

**File:** contracts/LRTWithdrawalManager.sol (L809-809)
```text
            unlockedWithdrawalsCount[asset]++;
```

**File:** contracts/LRTWithdrawalManager.sol (L877-879)
```text
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
```
