### Title
Interest-Exclusion Cap in `_withdrawFromAave` Causes Temporary Freeze of ETH Withdrawals When `expectedAssetAmount` Exceeds Principal — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`_withdrawFromAave` hard-caps the amount it will withdraw to `totalETHDepositedToAave` (principal only). When Aave interest has accrued, a user whose `expectedAssetAmount` falls in the range `(totalETHDepositedToAave, aaveBalance]` will have their `completeWithdrawal` call permanently revert with `InsufficientLiquidityForWithdrawal`, even though the contract holds sufficient total ETH (principal + interest) to cover the request. The user's rsETH has already been burned at `unlockQueue` time, so they are left with no rsETH and no ETH until external intervention occurs.

---

### Finding Description

**Root cause — `_withdrawFromAave` (line 912):**

```solidity
uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave
    ? aaveBalance
    : totalETHDepositedToAave;                          // capped at principal

withdrawnAmount = amount > withdrawablePrincipal
    ? withdrawablePrincipal                             // silently truncated
    : amount;
``` [1](#0-0) 

When `aaveBalance > totalETHDepositedToAave` (interest has accrued), `withdrawablePrincipal = totalETHDepositedToAave`. Any request for `amount > totalETHDepositedToAave` is silently truncated to `totalETHDepositedToAave` and the function returns without error.

**Failure path — `_processWithdrawalCompletion` (lines 720–731):**

```solidity
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);                // withdraws only principal

        uint256 balanceAfter = address(this).balance;
        if (balanceAfter < request.expectedAssetAmount) {
            revert InsufficientLiquidityForWithdrawal(); // always fires
        }
    }
}
``` [2](#0-1) 

**Concrete scenario (all values in wei):**

| Variable | Value |
|---|---|
| `totalETHDepositedToAave` | `P` |
| `aaveBalance` | `P + I` (I ≥ 1, interest accrued) |
| `contractBalance` | `0` (all ETH auto-deposited to Aave) |
| `request.expectedAssetAmount` | `P + 1` |

1. `contractBalance (0) < P + 1` → enter Aave branch
2. `amountNeeded = P + 1`
3. `_withdrawFromAave(P + 1)` → `withdrawablePrincipal = P` → withdraws `P`
4. `balanceAfter = P`
5. `P < P + 1` → **`revert InsufficientLiquidityForWithdrawal`**

The contract holds `P + I ≥ P + 1` total ETH, yet the withdrawal fails. Because Solidity reverts all state changes, the user's request survives intact and every subsequent retry produces the same revert.

**rsETH is already burned.** `expectedAssetAmount` is finalized and rsETH is burned during `unlockQueue` → `_unlockWithdrawalRequests`, before `completeWithdrawal` is ever called. [3](#0-2) 

The user has surrendered their rsETH and cannot recover it through any user-facing function.

**`expectedAssetAmount` can naturally land in the problematic range.** It is set by oracle prices at `unlockQueue` time via `_calculatePayoutAmount`:

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
``` [4](#0-3) 

There is no mechanism that prevents `payoutAmount` from falling in `(totalETHDepositedToAave, aaveBalance]`. This is a normal arithmetic outcome whenever the oracle-derived payout slightly exceeds the tracked principal.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

The user's ETH withdrawal is blocked indefinitely until external ETH arrives in the contract (e.g., via the `receive()` function at line 135, or from another unstaking vault transfer). The user's rsETH is already burned; they cannot re-enter the queue. The freeze is not permanent because anyone (including the user) can send a small amount of ETH directly to the contract to unblock it, but this requires awareness of the issue and is not part of the documented withdrawal flow. [5](#0-4) 

Note: calling `emergencyWithdrawFromAave` or `setAaveIntegrationEnabled(false)` does **not** fix the issue — both call `_collectInterestToTreasury()` first (sending the interest away), then call `_withdrawFromAave` which again caps at principal, leaving the contract 1 wei short. [6](#0-5) 

---

### Likelihood Explanation

**Medium.** The preconditions are all normal operating states:
- Aave integration is enabled (intended production use)
- Interest accrues continuously on any non-zero Aave balance
- `unlockQueue` auto-deposits idle ETH to Aave, so `contractBalance = 0` is the steady state
- Oracle-derived `payoutAmount` landing in `(totalETHDepositedToAave, aaveBalance]` is an ordinary arithmetic outcome; no manipulation is required

The window grows over time as interest accumulates. Any user whose withdrawal is unlocked while `payoutAmount > totalETHDepositedToAave` is affected.

---

### Recommendation

In `_withdrawFromAave`, remove the principal-only cap when the caller is the withdrawal completion path, or allow the function to withdraw up to `aaveBalance` (including interest) when needed to satisfy a user withdrawal. The interest-segregation intent should be enforced at the `_collectInterestToTreasury` call site, not by silently truncating user withdrawals.

Alternatively, in `_processWithdrawalCompletion`, after `_withdrawFromAave` returns, check whether the shortfall is covered by accrued interest and withdraw the remainder directly:

```solidity
// If still short, use accrued interest to cover the gap
if (balanceAfter < request.expectedAssetAmount) {
    uint256 remaining = request.expectedAssetAmount - balanceAfter;
    aaveWETHGateway.withdrawETH(aavePool, remaining, address(this));
    balanceAfter = address(this).balance;
    if (balanceAfter < request.expectedAssetAmount) {
        revert InsufficientLiquidityForWithdrawal();
    }
}
```

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Foundry fork test (mainnet fork or local mock)
// Preconditions:
//   totalETHDepositedToAave = P
//   aaveBalance = P + 1 wei  (1 wei of interest accrued)
//   contractBalance = 0
//   request.expectedAssetAmount = P + 1

function test_interestCapFreezesWithdrawal() public {
    uint256 P = 100 ether;

    // 1. Deposit P ETH to Aave
    vm.deal(address(withdrawalManager), P);
    vm.prank(operator);
    withdrawalManager.depositIdleETHToAave(P);
    // totalETHDepositedToAave == P, aaveBalance == P

    // 2. Simulate 1 wei of interest accruing (aWETH rebases)
    _simulateAaveInterest(1); // aaveBalance = P + 1

    // 3. User initiates withdrawal for rsETH amount that maps to P + 1 ETH
    uint256 rsETHAmount = _rsETHForETH(P + 1);
    vm.prank(user);
    withdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "");

    // 4. Operator unlocks the queue (burns rsETH, sets expectedAssetAmount = P + 1)
    vm.roll(block.number + withdrawalDelayBlocks + 1);
    vm.prank(operator);
    withdrawalManager.unlockQueue(ETH_TOKEN, type(uint256).max, ...);

    // 5. User attempts to complete withdrawal — REVERTS
    vm.prank(user);
    vm.expectRevert(ILRTWithdrawalManager.InsufficientLiquidityForWithdrawal.selector);
    withdrawalManager.completeWithdrawal(ETH_TOKEN, "");

    // 6. Invariant: aaveBalance (P+1) >= expectedAssetAmount (P+1), yet withdrawal fails
    assertGe(withdrawalManager.getAaveBalance(), P + 1);
}
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L135-135)
```text
    receive() external payable { }
```

**File:** contracts/LRTWithdrawalManager.sol (L551-562)
```text
    function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

        uint256 withdrawnAmount = _withdrawFromAave(amount);

        emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
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

**File:** contracts/LRTWithdrawalManager.sol (L802-805)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

**File:** contracts/LRTWithdrawalManager.sol (L911-914)
```text
        // Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
```
