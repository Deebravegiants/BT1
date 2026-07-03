Audit Report

## Title
Push-ETH Pattern in `_processWithdrawalCompletion` Permanently Freezes Funds for Non-ETH-Receiving Contract Withdrawers — (File: `contracts/LRTWithdrawalManager.sol`)

## Summary

`_processWithdrawalCompletion` uses a push pattern to deliver ETH to the withdrawing user via `_transferAsset`, which performs a low-level `.call{value:}`. If the recipient is a smart contract that cannot receive ETH, the call returns `false`, `EthTransferFailed` is thrown, and the entire transaction reverts. Because rsETH is burned and ETH is redeemed from `LRTUnstakingVault` during the earlier `unlockQueue` call — not during `completeWithdrawal` — the ETH is already sitting inside `LRTWithdrawalManager` with no admin recovery path, resulting in permanent fund freezing.

## Finding Description

**Step 1 — rsETH burned and ETH redeemed during `unlockQueue`:**
`unlockQueue` (L305–307) burns rsETH and calls `unstakingVault.redeem(asset, assetAmountUnlocked)`, transferring ETH into `LRTWithdrawalManager` before any user-facing completion occurs. [1](#0-0) 

**Step 2 — `_processWithdrawalCompletion` pushes ETH to user:**
At L734, `_transferAsset(asset, user, request.expectedAssetAmount)` is called. For ETH, `_transferAsset` (L877–879) performs `payable(to).call{value: amount}("")` and reverts with `EthTransferFailed` if `sent == false`. [2](#0-1) [3](#0-2) 

**Step 3 — Full revert restores state, but ETH remains:**
Because the revert unwinds all state changes in `_processWithdrawalCompletion` (the `delete withdrawalRequests[requestId]` at L712, the `popFront` at L705, and the `unlockedWithdrawalsCount[asset]--` at L717), the withdrawal request is restored and `unlockedWithdrawalsCount[asset]` remains ≥ 1. The ETH, however, is already in the contract from `unlockQueue` and cannot be recovered. [4](#0-3) 

**Step 4 — `completeWithdrawalForUser` provides no escape:**
The operator path `completeWithdrawalForUser` (L192–204) calls the same `_processWithdrawalCompletion(asset, user, referralId)` with the same `user` address, so it hits the identical revert. [5](#0-4) 

**Step 5 — `sweepRemainingAssets` is permanently blocked:**
`sweepRemainingAssets` (L403) gates on `hasUnlockedWithdrawals(asset)`, which returns `true` as long as `unlockedWithdrawalsCount[asset] > 0`. The stuck request keeps this counter positive indefinitely. [6](#0-5) 

No admin function exists to redirect the ETH to an alternate address or force-delete the stuck request.

## Impact Explanation

**Critical — Permanent freezing of funds.** The user's rsETH is irreversibly burned during `unlockQueue`. The ETH equivalent is locked inside `LRTWithdrawalManager` with no on-chain recovery path: `completeWithdrawal` and `completeWithdrawalForUser` both revert for the affected user, and `sweepRemainingAssets` is blocked while any unlocked withdrawal exists. This matches the allowed Critical impact class "Permanent freezing of funds."

## Likelihood Explanation

**Low.** The affected depositor must be a smart contract without a functional ETH `receive()` or `fallback()`. Realistic cases include multisig wallets lacking an ETH fallback, DeFi aggregators or vaults that route withdrawals through a contract, or contracts upgraded post-initiation to remove ETH acceptance. The scenario is uncommon but entirely plausible given that the protocol accepts smart-contract depositors. No attacker capability is required — the victim triggers the freeze by attempting their own legitimate withdrawal.

## Recommendation

Replace the push-ETH pattern with a pull (claim) pattern for ETH withdrawals:

1. In `_processWithdrawalCompletion`, instead of calling `_transferAsset(asset, user, amount)` for ETH, credit `pendingETHClaims[user] += amount` and emit an event.
2. Add a separate `claimETH()` function that lets the user pull their credited balance at will.
3. Apply the same pattern to the `feeRecipient` transfer in `instantWithdrawal` (L246) and to `_collectInterestToTreasury` (L957).

This eliminates the ability of any single recipient's ETH-rejection behavior to block withdrawal execution or freeze funds.

## Proof of Concept

1. Deploy a smart contract `VaultProxy` with no `receive()` function.
2. `VaultProxy` calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. rsETH is burned (L305); ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager` (L307). `unlockedWithdrawalsCount[ETH_TOKEN]` becomes 1.
4. `VaultProxy` calls `completeWithdrawal(ETH_TOKEN, "")`. `_processWithdrawalCompletion` reaches `_transferAsset(ETH_TOKEN, VaultProxy, amount)` at L734.
5. `payable(VaultProxy).call{value: amount}("")` returns `(false, "")`. `EthTransferFailed` is thrown; entire transaction reverts. Withdrawal request is restored.
6. Operator calls `completeWithdrawalForUser(ETH_TOKEN, VaultProxy, "")` — same revert path.
7. `unlockedWithdrawalsCount[ETH_TOKEN]` remains 1; `sweepRemainingAssets` reverts with `PendingWithdrawalsExist`.
8. `VaultProxy`'s rsETH is permanently burned; the ETH equivalent is permanently locked in `LRTWithdrawalManager`.

**Foundry test sketch:**
```solidity
contract NoReceive {} // no receive() or fallback()

function test_permanentFreeze() public {
    NoReceive victim = new NoReceive();
    // fund victim with rsETH, initiate withdrawal, run unlockQueue,
    // then assert completeWithdrawal reverts with EthTransferFailed
    // and sweepRemainingAssets reverts with PendingWithdrawalsExist
}
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L192-203)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L402-403)
```text
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```

**File:** contracts/LRTWithdrawalManager.sol (L712-717)
```text
        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;
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
