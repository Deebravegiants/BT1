### Title
Admin can update rsETH token address while withdrawals are pending, permanently freezing queued rsETH in `LRTWithdrawalManager` — (File: contracts/LRTConfig.sol)

---

### Summary
`LRTConfig.setRSETH()` allows the `DEFAULT_ADMIN_ROLE` to replace the rsETH token address at any time with no check for pending withdrawal requests. When users call `initiateWithdrawal()`, their rsETH (old token) is transferred into `LRTWithdrawalManager`. If the rsETH address is updated before `unlockQueue()` processes those requests, the burn call inside `unlockQueue()` targets the new rsETH contract — which `LRTWithdrawalManager` holds zero balance of — causing a permanent revert and freezing all queued rsETH and the corresponding LST withdrawals.

---

### Finding Description

**Root cause — `LRTConfig.setRSETH()`:** [1](#0-0) 

The function performs no check on whether `LRTWithdrawalManager` currently holds rsETH tokens belonging to in-flight withdrawal requests.

**Step 1 — rsETH is pulled into `LRTWithdrawalManager` on `initiateWithdrawal()`:** [2](#0-1) 

The old rsETH tokens are now custodied by `LRTWithdrawalManager` and cannot be recovered by the user.

**Step 2 — `unlockQueue()` burns rsETH using the *current* `lrtConfig.rsETH()` address:** [3](#0-2) 

If `setRSETH()` was called between steps 1 and 2, `lrtConfig.rsETH()` now returns the new token address. `LRTWithdrawalManager` holds zero balance of the new token, so `burnFrom` reverts with an ERC20 insufficient-balance error. Every subsequent call to `unlockQueue()` for any asset will revert at this line as long as there is any rsETH to burn, making it impossible to process any queued withdrawal.

**No guard exists** — unlike `updateAssetStrategy()`, which explicitly checks that no NDC funds remain before allowing the update: [4](#0-3) 

`setRSETH()` has no analogous protection.

---

### Impact Explanation

**Permanent freezing of funds.** Users who called `initiateWithdrawal()` have already surrendered their rsETH to `LRTWithdrawalManager`. After the rsETH address swap:

- `unlockQueue()` reverts on every call (burn of new rsETH fails).
- `completeWithdrawal()` is gated behind `unlockQueue()` having advanced `nextLockedNonce`, so users can never reach the asset-transfer step.
- The old rsETH tokens are stranded in `LRTWithdrawalManager` with no rescue path (no sweep function exists for rsETH itself).
- All committed LST amounts (`assetsCommitted[asset]`) remain locked and unavailable.

If the protocol has already migrated to the new rsETH (the common upgrade scenario), reverting `setRSETH()` back to the old address is operationally undesirable and may not be possible if the old token is deprecated, making the freeze permanent.

---

### Likelihood Explanation

**Low.** The trigger is a legitimate admin action — updating the rsETH address during a protocol upgrade — not a malicious one. Because `LRTWithdrawalManager` is designed to hold queued rsETH continuously during normal operation, any rsETH token migration performed without first draining the withdrawal queue will hit this condition. The absence of a guard (unlike the analogous `updateAssetStrategy()` check) means the risk is latent in every future upgrade cycle.

---

### Recommendation

Mirror the guard pattern already used in `updateAssetStrategy()`. Before allowing `setRSETH()` to proceed, verify that `LRTWithdrawalManager` holds no rsETH balance (i.e., no in-flight withdrawal requests exist):

```solidity
function setRSETH(address rsETH_) external onlyRole(DEFAULT_ADMIN_ROLE) {
    UtilLib.checkNonZeroAddress(rsETH_);
    // Ensure no rsETH is custodied in the withdrawal manager
    address withdrawalManager = contractMap[LRTConstants.LRT_WITHDRAW_MANAGER];
    if (withdrawalManager != address(0)) {
        uint256 pendingRsETH = IERC20(rsETH).balanceOf(withdrawalManager);
        if (pendingRsETH > 0) revert CannotUpdateRsETHWithPendingWithdrawals(pendingRsETH);
    }
    rsETH = rsETH_;
    emit SetRSETH(rsETH_);
}
```

---

### Proof of Concept

1. Alice calls `LRTWithdrawalManager.initiateWithdrawal(stETH, 100e18)`.
   - `IERC20(oldRsETH).safeTransferFrom(Alice, LRTWithdrawalManager, 100e18)` succeeds.
   - `LRTWithdrawalManager` now holds 100 old rsETH tokens.

2. Admin calls `LRTConfig.setRSETH(newRsETH)` as part of a protocol upgrade.
   - `lrtConfig.rsETH()` now returns `newRsETH`.

3. Operator calls `LRTWithdrawalManager.unlockQueue(stETH, ...)`.
   - Reaches line 305: `IRSETH(newRsETH).burnFrom(LRTWithdrawalManager, 100e18)`.
   - `LRTWithdrawalManager.balanceOf(newRsETH) == 0` → ERC20 revert.
   - `unlockQueue()` reverts. Alice's withdrawal is permanently stuck.

4. Alice's 100 old rsETH tokens remain frozen in `LRTWithdrawalManager` with no recovery path.

### Citations

**File:** contracts/LRTConfig.sol (L151-166)
```text
        if (assetStrategy[asset] != address(0)) {
            // get ndcs
            address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);
            address[] memory ndcs = ILRTDepositPool(depositPool).getNodeDelegatorQueue();

            uint256 length = ndcs.length;
            for (uint256 i = 0; i < length;) {
                uint256 ndcBalance = IStrategy(assetStrategy[asset]).userUnderlyingView(ndcs[i]);
                if (ndcBalance > 0) {
                    revert CannotUpdateStrategyAsItHasFundsNDCFunds(ndcs[i], ndcBalance);
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** contracts/LRTConfig.sol (L215-219)
```text
    function setRSETH(address rsETH_) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(rsETH_);
        rsETH = rsETH_;
        emit SetRSETH(rsETH_);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L305-305)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
```
