Audit Report

## Title
ETH Permanently Frozen When Withdrawer Is a Contract Without `receive()` Function - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTWithdrawalManager._transferAsset()` pushes ETH via a raw `.call{value: amount}("")`. If the recipient is a contract without a `receive()` or `fallback()` function, the call fails and the entire `_processWithdrawalCompletion()` transaction reverts, restoring the withdrawal request. Because rsETH was already burned and ETH already moved into `LRTWithdrawalManager` during the prior `unlockQueue()` transaction, the ETH is permanently stranded with no admin rescue path.

## Finding Description
The withdrawal lifecycle spans two separate transactions:

**Transaction 1 — `unlockQueue()`**: rsETH held by the contract is burned and ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager`. These state changes are committed and irreversible.

```solidity
// contracts/LRTWithdrawalManager.sol L305-307
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
unstakingVault.redeem(asset, assetAmountUnlocked);
```

**Transaction 2 — `completeWithdrawal()` / `completeWithdrawalForUser()`**: Calls `_processWithdrawalCompletion()`, which mutates state (pops nonce, deletes request, decrements `unlockedWithdrawalsCount`) and then calls `_transferAsset()`:

```solidity
// contracts/LRTWithdrawalManager.sol L699-734
uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
// ...
delete withdrawalRequests[requestId];
// ...
unlockedWithdrawalsCount[asset]--;
// ...
_transferAsset(asset, user, request.expectedAssetAmount);
```

```solidity
// contracts/LRTWithdrawalManager.sol L876-883
function _transferAsset(address asset, address to, uint256 amount) internal {
    if (asset == LRTConstants.ETH_TOKEN) {
        (bool sent,) = payable(to).call{ value: amount }("");
        if (!sent) revert EthTransferFailed();
    } else {
        IERC20(asset).safeTransfer(to, amount);
    }
}
```

If `to` is a contract without `receive()`, the `.call` returns `false`, `EthTransferFailed` is thrown, and the entire transaction reverts — restoring the nonce, the request, and the `unlockedWithdrawalsCount`. Every subsequent call to `completeWithdrawal()` or `completeWithdrawalForUser()` reverts identically because both always send to `user`.

The only admin escape valve, `sweepRemainingAssets()`, is gated:

```solidity
// contracts/LRTWithdrawalManager.sol L403
if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```

```solidity
// contracts/LRTWithdrawalManager.sol L629-631
function hasUnlockedWithdrawals(address asset) public view returns (bool hasUnlocked) {
    return unlockedWithdrawalsCount[asset] > 0;
}
```

Because the revert restores `unlockedWithdrawalsCount[asset]` to its pre-call value (> 0), `sweepRemainingAssets()` is permanently blocked for this asset. There is no alternative admin path to redirect ETH to a different address.

## Impact Explanation
**Critical — Permanent freezing of funds.** A smart-contract caller without a `receive()` function loses both assets simultaneously: rsETH is burned in `unlockQueue()` (a committed transaction) and the corresponding ETH is permanently locked in `LRTWithdrawalManager` with no recovery mechanism. This matches the allowed impact class "Permanent freezing of funds."

## Likelihood Explanation
**Medium.** Smart-contract wallets (e.g., Gnosis Safe with custom modules), protocol-owned treasuries, DAO vaults, and DeFi integrations routinely interact with staking protocols. Many such contracts do not implement a `receive()` function. `initiateWithdrawal()` accepts any `msg.sender` without checking ETH receivability, and the protocol provides no warning. The scenario requires no attacker — a legitimate user triggers it by normal use of the withdrawal flow.

## Recommendation
1. **Pull-payment pattern (preferred)**: Replace the ETH push in `_processWithdrawalCompletion()` with a credit to a claimable balance mapping. Add a separate `claimETH()` function that lets the user pull funds to any address they specify. This fully decouples delivery failure from state mutation.
2. **WETH fallback**: If the ETH `.call` fails, wrap the ETH as WETH and credit it to the user's address via `safeTransfer`, ensuring the user can always retrieve value regardless of `receive()` support.
3. **Alternate recipient at claim time**: Allow `completeWithdrawal()` to accept an explicit `recipient` parameter so the user can redirect ETH to an EOA even if `msg.sender` cannot receive ETH.

## Proof of Concept
1. Deploy a smart-contract vault with no `receive()` or `fallback()` function.
2. The vault calls `initiateWithdrawal(ETH_TOKEN, 1 ether rsETH, "")` — rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)` — rsETH is burned (committed), ETH is moved from `LRTUnstakingVault` into `LRTWithdrawalManager` (committed).
4. The vault calls `completeWithdrawal(ETH_TOKEN, "")`. Inside `_processWithdrawalCompletion()`, `_transferAsset()` executes `payable(vault).call{value: amount}("")`, which returns `false`. `EthTransferFailed` reverts the transaction, restoring all state in step 4.
5. Repeat step 4 indefinitely — every call reverts identically.
6. Admin calls `sweepRemainingAssets(ETH_TOKEN)` — reverts with `PendingWithdrawalsExist` because `unlockedWithdrawalsCount[ETH_TOKEN] > 0`.
7. Result: rsETH permanently burned, ETH permanently locked in `LRTWithdrawalManager`.

**Foundry test sketch**:
```solidity
contract NoReceive { /* no receive() */ }

function test_ethFrozenNoReceive() public {
    NoReceive vault = new NoReceive();
    // fund vault with rsETH, approve LRTWithdrawalManager
    vm.prank(address(vault));
    withdrawalManager.initiateWithdrawal(ETH_TOKEN, 1 ether, "");
    // operator unlocks
    vm.prank(operator);
    withdrawalManager.unlockQueue(ETH_TOKEN, ...);
    // attempt completion — must revert
    vm.prank(address(vault));
    vm.expectRevert(LRTWithdrawalManager.EthTransferFailed.selector);
    withdrawalManager.completeWithdrawal(ETH_TOKEN, "");
    // sweep must also revert
    vm.prank(manager);
    vm.expectRevert(LRTWithdrawalManager.PendingWithdrawalsExist.selector);
    withdrawalManager.sweepRemainingAssets(ETH_TOKEN);
}
```