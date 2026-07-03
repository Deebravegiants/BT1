### Title
ETH Withdrawal Permanently Frozen When User's Contract Address Becomes Unable to Receive ETH — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

The `LRTWithdrawalManager` two-phase withdrawal design burns rsETH in `unlockQueue` and only later delivers ETH in `completeWithdrawal`. The ETH delivery is a raw `.call{value}` to the stored `user` address. If that address is a smart contract that rejects ETH at claim time, the delivery reverts permanently. Because rsETH is already destroyed and no admin escape hatch exists, the ETH is frozen in the contract forever.

---

### Finding Description

The withdrawal lifecycle has two distinct, non-atomic phases:

**Phase 1 — `unlockQueue` (operator-triggered):**
rsETH held by the contract is burned and the corresponding ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`. [1](#0-0) 

After this call, the rsETH no longer exists. The ETH now sits in `LRTWithdrawalManager`.

**Phase 2 — `completeWithdrawal` / `completeWithdrawalForUser` (user or operator-triggered):**
`_processWithdrawalCompletion` attempts to deliver the ETH to the stored `user` address: [2](#0-1) 

The delivery is performed by `_transferAsset`: [3](#0-2) 

If `user` is a smart contract whose `receive`/`fallback` reverts (e.g., an upgradeable wallet that was modified, or a contract redeployed at the same address after `selfdestruct`), the `.call` returns `false` and the function reverts with `EthTransferFailed`. Because the entire transaction reverts, the withdrawal record is preserved and `unlockedWithdrawalsCount[asset]` remains non-zero.

**No recovery path exists:**

- `sweepRemainingAssets` is gated by `!hasUnlockedWithdrawals(asset)`, which checks `unlockedWithdrawalsCount[asset] > 0`. Since the stuck withdrawal keeps this counter elevated, the sweep is permanently blocked.
- There is no admin function to redirect a stuck ETH withdrawal to an alternate address.
- There is no `cancelWithdrawal` function to return rsETH (it is already burned).

The `completeWithdrawalForUser` operator path suffers the same failure because it calls the same `_processWithdrawalCompletion` with the same `user` address. [4](#0-3) 

The developers acknowledge ETH delivery risk in the `completeWithdrawalForUser` NatSpec ("Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH"), but this comment only addresses transient gas-grief, not the permanent rejection case where rsETH is already destroyed.

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

Once `unlockQueue` burns the rsETH and moves ETH into `LRTWithdrawalManager`, the user has no rsETH left. If `completeWithdrawal` can never succeed (because the destination contract permanently rejects ETH), the user loses both their rsETH (burned) and their ETH (frozen). There is no on-chain mechanism for the protocol to recover or redirect the frozen ETH.

---

### Likelihood Explanation

**Low.**

The scenario requires the withdrawing address to be a smart contract (not an EOA) that, between the time `initiateWithdrawal` is called and `completeWithdrawal` is attempted, becomes unable to receive ETH. Realistic triggers include:

- An upgradeable smart contract wallet whose implementation is changed to remove `receive()`.
- A contract that calls `selfdestruct` and is redeployed at the same address (possible pre-Cancun, and via CREATE2 post-Cancun in some configurations) with no ETH receiver.
- A multisig or account-abstraction wallet whose guard logic begins reverting on ETH receipt.

Smart contract wallets are increasingly common among large rsETH holders, making this a realistic edge case rather than a purely theoretical one.

---

### Recommendation

1. **Pull-payment pattern**: Instead of pushing ETH to `user` in `completeWithdrawal`, credit the amount to a per-user claimable balance mapping and let users pull it with a separate `claimETH()` call that they can direct to any address they control.

2. **Alternate recipient**: Allow users to specify a `recipient` address at claim time (distinct from the initiating address), so a stuck smart contract wallet can redirect ETH to an EOA.

3. **Admin rescue**: Add a privileged function (e.g., `rescueStuckWithdrawal(asset, user, alternateRecipient)`) that can redirect a permanently stuck ETH withdrawal to a different address, callable only after a timeout and only by a high-privilege role (e.g., `TIMELOCK_ROLE`).

---

### Proof of Concept

```
1. Alice deploys an upgradeable proxy wallet `W` that has a `receive()` function.

2. Alice calls LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")
   from address W.
   → rsETH is transferred from W to LRTWithdrawalManager.
   → userAssociatedNonces[ETH_TOKEN][W] records the nonce.

3. Operator calls unlockQueue(ETH_TOKEN, ...).
   → rsETH held by LRTWithdrawalManager is burned (line 305).
   → ETH is pulled from LRTUnstakingVault into LRTWithdrawalManager (line 307).
   → Alice's rsETH is now gone.

4. Alice (or an attacker who compromised W) upgrades W's implementation to
   remove receive(), causing all ETH transfers to revert.

5. Alice calls LRTWithdrawalManager.completeWithdrawal(ETH_TOKEN, "").
   → _processWithdrawalCompletion is called with user = W.
   → _transferAsset calls payable(W).call{value: amount}("").
   → W rejects ETH → sent == false → revert EthTransferFailed().
   → Transaction reverts; withdrawal record is restored.

6. Operator calls completeWithdrawalForUser(ETH_TOKEN, W, "").
   → Same failure.

7. unlockedWithdrawalsCount[ETH_TOKEN] > 0 forever.
   → sweepRemainingAssets reverts with PendingWithdrawalsExist().

Result: Alice's ETH is permanently frozen in LRTWithdrawalManager.
        Alice's rsETH is permanently destroyed.
        No on-chain recovery path exists.
```

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L734-734)
```text
        _transferAsset(asset, user, request.expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L876-883)
```text
    function _transferAsset(address asset, address to, uint256 amount) internal {
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
        } else {
            IERC20(asset).safeTransfer(to, amount);
        }
    }
```
