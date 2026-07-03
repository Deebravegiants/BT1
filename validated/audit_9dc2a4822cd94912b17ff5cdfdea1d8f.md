### Title
Aave WETH Liquidity Exhaustion Blocks All ETH Withdrawal Completion and Disables Admin Recovery — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

When `isAaveIntegrationEnabled` is `true` and the Aave WETH pool reaches 100% utilization, `_withdrawFromAave` propagates an uncaught revert through `_processWithdrawalCompletion`, blocking every ETH `completeWithdrawal` call. Critically, every admin recovery path (`emergencyWithdrawFromAave`, `setAaveIntegrationEnabled(false)`) routes through the same unguarded `_withdrawFromAave`, so the integration cannot be disabled and the freeze cannot be lifted by the protocol until Aave liquidity independently recovers.

---

### Finding Description

**Entrypoint:** `completeWithdrawal` → `_processWithdrawalCompletion`

In `_processWithdrawalCompletion`, when the contract's native ETH balance is insufficient to cover a request, it calls `_withdrawFromAave` with no `try/catch`: [1](#0-0) 

Inside `_withdrawFromAave`, the call to `aaveWETHGateway.withdrawETH` is also unguarded: [2](#0-1) 

If the Aave WETH pool has zero available liquidity (all WETH is borrowed by external users), `withdrawETH` reverts. Because there is no `try/catch` at either call site, the revert propagates all the way up, causing `completeWithdrawal` to revert. Since the entire transaction is atomic, the user's queue entry is rolled back and the request remains stuck — but it cannot be completed until Aave liquidity recovers.

**All admin escape hatches are equally blocked:**

1. `emergencyWithdrawFromAave` — calls `_withdrawFromAave` directly; reverts under the same condition: [3](#0-2) 

2. `setAaveIntegrationEnabled(false)` — calls `_withdrawFromAave(aaveBalance)` before setting `isAaveIntegrationEnabled = false`; if it reverts, the flag is never cleared and the integration cannot be disabled: [4](#0-3) 

There is no code path that allows ETH withdrawals to proceed from the contract's own balance while `isAaveIntegrationEnabled` remains `true`, and there is no code path that sets `isAaveIntegrationEnabled = false` without first successfully draining Aave.

---

### Impact Explanation

**Impact: Medium — Temporary freezing of funds.**

All ETH withdrawal completions are blocked for every user whose request requires pulling from Aave. The freeze persists for as long as Aave WETH utilization remains at or near 100%. Aave's variable interest rate model creates strong economic incentives for borrowers to repay at extreme utilization, making a truly permanent freeze unlikely in practice. The correct classification is therefore **temporary** (not permanent) freezing of funds.

---

### Likelihood Explanation

Aave WETH utilization reaching 100% is a realistic, historically observed market condition (e.g., during periods of high ETH demand or market stress). No attacker action is required — it is a passive market condition. The protocol has no on-chain mechanism to respond until liquidity recovers externally.

---

### Recommendation

1. **Wrap `_withdrawFromAave` in `_processWithdrawalCompletion` with `try/catch`** and revert with `InsufficientLiquidityForWithdrawal` only after the catch, so the revert message is controlled and the path is explicit.

2. **Decouple `setAaveIntegrationEnabled(false)` from `_withdrawFromAave`**: allow the flag to be set to `false` unconditionally, and handle the Aave balance drain separately (e.g., via a subsequent `emergencyWithdrawFromAave` call once liquidity recovers). This restores the admin's ability to fall back to direct ETH balance for user withdrawals.

3. **Add a partial-withdrawal fallback**: if `_withdrawFromAave` returns less than `amountNeeded` (e.g., due to liquidity constraints), check whether `address(this).balance` is now sufficient before reverting, rather than propagating the Aave revert blindly.

---

### Proof of Concept

```solidity
// Fork mainnet at a block where Aave WETH utilization is near 100%,
// or manipulate a local fork to borrow all WETH from the Aave pool.

// 1. Operator calls unlockQueue for ETH, depositing unlocked ETH to Aave via depositToAaveExternal.
//    After this, address(this).balance < any pending request.expectedAssetAmount,
//    and all ETH is held as aWETH.

// 2. Simulate Aave WETH pool at 100% utilization:
//    vm.prank(whale);
//    aavePool.borrow(WETH, aavePool.getReserveData(WETH).availableLiquidity, 2, 0, whale);

// 3. User calls completeWithdrawal(ETH_TOKEN, ""):
//    → _processWithdrawalCompletion
//    → address(this).balance < request.expectedAssetAmount  (true)
//    → _withdrawFromAave(amountNeeded)
//    → aaveWETHGateway.withdrawETH(...)  ← REVERTS (no liquidity)
//    → completeWithdrawal REVERTS

// 4. PAUSER calls emergencyWithdrawFromAave(type(uint256).max):
//    → _withdrawFromAave(amount)
//    → aaveWETHGateway.withdrawETH(...)  ← REVERTS

// 5. Manager calls setAaveIntegrationEnabled(false):
//    → _withdrawFromAave(aaveBalance)
//    → aaveWETHGateway.withdrawETH(...)  ← REVERTS
//    → isAaveIntegrationEnabled remains true

// All three paths revert. ETH withdrawals are frozen until Aave liquidity recovers.
assertEq(withdrawalManager.isAaveIntegrationEnabled(), true); // never cleared
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L494-503)
```text
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
                }
            }

            // Revoke approval for aWETH token to Aave WETH Gateway
            _revokeApprovalToAaveWETHGateway();
        }

        isAaveIntegrationEnabled = enabled;
```

**File:** contracts/LRTWithdrawalManager.sol (L560-560)
```text
        uint256 withdrawnAmount = _withdrawFromAave(amount);
```

**File:** contracts/LRTWithdrawalManager.sol (L720-731)
```text
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L917-917)
```text
        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
```
