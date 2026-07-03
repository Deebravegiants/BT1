### Title
Accrued Aave Interest Permanently Inaccessible for User Withdrawals When `totalETHDepositedToAave` Reaches Zero — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`_withdrawFromAave` caps the withdrawable amount at `min(aaveBalance, totalETHDepositedToAave)`. When all principal has been withdrawn through the normal `completeWithdrawal` path — which calls `_withdrawFromAave` without first collecting interest — `totalETHDepositedToAave` reaches zero while `aaveBalance` still holds accrued interest. Every subsequent `completeWithdrawal` for ETH then silently gets 0 ETH from Aave and reverts with `InsufficientLiquidityForWithdrawal`, permanently blocking those withdrawals and freezing the interest in Aave.

---

### Finding Description

**`_withdrawFromAave` principal cap (lines 912–915):**

```solidity
uint256 withdrawablePrincipal =
    aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
if (withdrawnAmount == 0) return 0;   // silent zero-return
``` [1](#0-0) 

When `totalETHDepositedToAave == 0`, `withdrawablePrincipal = 0` regardless of `aaveBalance`, so the function returns 0 silently.

**`_processWithdrawalCompletion` calls `_withdrawFromAave` without collecting interest first (lines 720–730):**

```solidity
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);          // no _collectInterestToTreasury() call

        uint256 balanceAfter = address(this).balance;
        if (balanceAfter < request.expectedAssetAmount) {
            revert InsufficientLiquidityForWithdrawal();
        }
    }
}
``` [2](#0-1) 

Contrast this with every other caller of `_withdrawFromAave` (`emergencyWithdrawFromAave`, `setAaveIntegrationEnabled`, `configureAaveIntegration`), all of which call `_collectInterestToTreasury()` first. [3](#0-2) 

**Concrete state transition:**

| Step | `totalETHDepositedToAave` | `aaveBalance` |
|------|--------------------------|---------------|
| 100 ETH deposited to Aave | 100 | 100 |
| Interest accrues | 100 | 101 |
| User A completes withdrawal for 100 ETH: `_withdrawFromAave(100)` → `withdrawablePrincipal = min(101,100) = 100`, withdraws 100 | **0** | **1** |
| User B tries to complete withdrawal for 1 ETH: `_withdrawFromAave(1)` → `withdrawablePrincipal = min(1,0) = 0`, returns 0 | 0 | 1 |
| `balanceAfter < 1` → `revert InsufficientLiquidityForWithdrawal` | — | — |

**Recovery paths are also broken:**

- `collectInterestToTreasury` can drain the 1 ETH to treasury (not to users), but user withdrawals remain blocked.
- `emergencyWithdrawFromAave` calls `_collectInterestToTreasury()` first (draining `aaveBalance` to 0), then calls `_withdrawFromAave(amount)` which hits `if (aaveBalance == 0) revert InsufficientAaveBalance()` — the entire transaction reverts, so even this path fails. [4](#0-3) 

The interest is permanently inaccessible for user withdrawals and can only be routed to treasury, not to the users whose withdrawals are blocked.

---

### Impact Explanation

- **Permanent freezing of unclaimed yield**: Accrued Aave interest becomes permanently inaccessible for user ETH withdrawals. It can only be swept to treasury, not credited to waiting users.
- **Temporary freezing of user funds**: All ETH `completeWithdrawal` calls revert with `InsufficientLiquidityForWithdrawal` until an operator manually deposits fresh ETH into the contract (no permissionless recovery path exists).

Scoped impact: **Medium — Permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

This is a natural, inevitable consequence of normal protocol operation — no attacker is required. Whenever the last principal withdrawal leaves any non-zero interest in Aave (which is always true if any time has elapsed since deposit), `totalETHDepositedToAave` reaches zero while `aaveBalance > 0`. Any subsequent ETH `completeWithdrawal` that needs to pull from Aave will be permanently blocked. The likelihood is **high** given that Aave interest accrues continuously and `_processWithdrawalCompletion` never collects it before withdrawing principal.

---

### Recommendation

In `_processWithdrawalCompletion`, call `_collectInterestToTreasury()` before `_withdrawFromAave` — consistent with every other call site:

```solidity
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        _collectInterestToTreasury();                          // collect interest first
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);
        ...
    }
}
```

Alternatively, allow `_withdrawFromAave` to use the full `aaveBalance` (not just `totalETHDepositedToAave`) when `totalETHDepositedToAave == 0`, or add a guard that prevents `totalETHDepositedToAave` from underflowing below the remaining `aaveBalance`.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

// Foundry fork test (Ethereum mainnet fork)
// Run: forge test --match-test test_interestFreezesWithdrawals -vvv

contract AaveInterestFreezePoC is Test {
    LRTWithdrawalManager wm;
    // ... setup: deploy protocol, configure Aave, create two users

    function test_interestFreezesWithdrawals() public {
        // 1. Deposit 100 ETH to Aave via the withdrawal manager
        vm.deal(address(wm), 100 ether);
        vm.prank(operator);
        wm.depositIdleETHToAave(100 ether);
        // totalETHDepositedToAave = 100, aaveBalance ≈ 100

        // 2. Simulate interest accrual (advance time, or directly mint aWETH to wm)
        vm.warp(block.timestamp + 365 days);
        // aaveBalance ≈ 101 (1 ETH interest)

        // 3. Unlock and complete User A's withdrawal for 100 ETH
        // (setup: userA has an unlocked withdrawal request for 100 ETH)
        vm.prank(userA);
        wm.completeWithdrawal(ETH_TOKEN, "");
        // totalETHDepositedToAave = 0, aaveBalance ≈ 1

        // 4. User B tries to complete their unlocked withdrawal for 1 ETH
        vm.prank(userB);
        vm.expectRevert(ILRTWithdrawalManager.InsufficientLiquidityForWithdrawal.selector);
        wm.completeWithdrawal(ETH_TOKEN, "");
        // Reverts even though 1 ETH of interest sits in Aave
    }
}
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L557-560)
```text
        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

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

**File:** contracts/LRTWithdrawalManager.sol (L908-909)
```text
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();
```

**File:** contracts/LRTWithdrawalManager.sol (L912-915)
```text
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;
```
