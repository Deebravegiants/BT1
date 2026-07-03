### Title
stETH Negative Rebase Between `unlockQueue` and `completeWithdrawal` Temporarily Freezes User Withdrawal Funds - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
The `LRTWithdrawalManager` stores a fixed `expectedAssetAmount` per withdrawal request at the time `unlockQueue` is called. Because stETH is a rebasing token, a negative rebase (slashing event) occurring after `unlockQueue` reduces the contract's actual stETH balance below the sum of all pending `expectedAssetAmount` values. The last users to call `completeWithdrawal` will find the balance insufficient and their transactions will revert, temporarily freezing their funds.

### Finding Description
`unlockQueue` pulls a precise amount of stETH from `LRTUnstakingVault` into `LRTWithdrawalManager` and records each user's `expectedAssetAmount`:

```solidity
// _unlockWithdrawalRequests sets the payout
request.expectedAssetAmount = payoutAmount;
...
// unlockQueue then redeems exactly assetAmountUnlocked from the vault
unstakingVault.redeem(asset, assetAmountUnlocked);
```

After this call, the withdrawal manager holds exactly `assetAmountUnlocked` stETH, and the sum of all unlocked `expectedAssetAmount` values equals `assetAmountUnlocked`. [1](#0-0) 

`completeWithdrawal` later transfers the stored amount directly to the user without re-checking the live balance:

```solidity
_transferAsset(asset, user, request.expectedAssetAmount);
``` [2](#0-1) 

`_transferAsset` for a non-ETH asset calls `IERC20(asset).safeTransfer(to, amount)`, which reverts if the contract's balance is insufficient. [3](#0-2) 

stETH is explicitly a supported withdrawal asset, confirmed by `initialize2` seeding `unlockedWithdrawalsCount` for `ST_ETH_TOKEN`: [4](#0-3) 

stETH is a rebasing token. Its balance in any holder address adjusts automatically at each daily oracle report. A negative rebase (validator slashing) reduces the withdrawal manager's stETH balance without updating any stored `expectedAssetAmount`. The internal bookkeeping is now higher than the actual balance, mirroring the FraxSwap pattern exactly.

### Impact Explanation
**Medium — Temporary freezing of funds.**

After a negative rebase, the withdrawal manager holds less stETH than the sum of all pending `expectedAssetAmount` values. Users who call `completeWithdrawal` are served in FIFO order (oldest nonce first). Early callers succeed; the last callers whose cumulative `expectedAssetAmount` exceeds the remaining balance receive a revert. Their rsETH has already been burned (at `initiateWithdrawal` time, rsETH was transferred to the manager; it is burned at `unlockQueue` time), so they cannot re-initiate. Their stETH is stuck in the contract until an operator manually replenishes the balance or a subsequent positive rebase restores it.

### Likelihood Explanation
**Low-Medium.** Ethereum validator slashing events are infrequent but have occurred historically (e.g., the Lido slashing incidents). The vulnerability window is the period between `unlockQueue` and the last `completeWithdrawal` call for a given batch, which can span multiple days given the 8-day withdrawal delay. A single slashing event during a large batch unlock is sufficient to trigger the freeze for the tail of the queue.

### Recommendation
- In `_processWithdrawalCompletion`, transfer `min(request.expectedAssetAmount, actualBalance)` rather than the stored amount unconditionally, and emit an event noting any shortfall.
- Alternatively, re-snapshot the live stETH balance at `completeWithdrawal` time and pro-rate payouts if the balance has decreased.
- At minimum, document that stETH negative rebases can temporarily block the last withdrawers in a batch and provide an operator recovery path (e.g., a function to top up the balance).

### Proof of Concept
1. Operator calls `unlockQueue(stETH, ...)` when the vault holds 100 stETH. Ten requests are unlocked, each with `expectedAssetAmount = 10 stETH`. The vault transfers 100 stETH to the withdrawal manager. [1](#0-0) 
2. A slashing event causes a 6% negative stETH rebase. The withdrawal manager's balance drops to ~94 stETH. No storage variable is updated.
3. Users 1–9 call `completeWithdrawal(stETH)`. Each receives 10 stETH. After 9 transfers, 4 stETH remain.
4. User 10 calls `completeWithdrawal(stETH)`. `_transferAsset` attempts `safeTransfer(user10, 10 stETH)`. The contract only holds 4 stETH → `safeTransfer` reverts. [3](#0-2) 
5. User 10's rsETH was already burned at `unlockQueue` time. Their 4 stETH is locked in the contract with no self-service recovery path.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L109-121)
```text
    function initialize2(
        uint256 unlockedWithdrawalsCountETHx,
        uint256 unlockedWithdrawalsCountSTETH,
        uint256 unlockedWithdrawalsCountETH
    )
        external
        reinitializer(2)
        onlyRole(LRTConstants.UNLOCKED_WITHDRAWAL_INITIALIZER)
    {
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN)] = unlockedWithdrawalsCountSTETH;
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ETHX_TOKEN)] = unlockedWithdrawalsCountETHx;
        unlockedWithdrawalsCount[LRTConstants.ETH_TOKEN] = unlockedWithdrawalsCountETH;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L301-307)
```text
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

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
