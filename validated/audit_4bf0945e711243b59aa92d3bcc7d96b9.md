### Title
aWETH Pre-Funding Breaks `_withdrawFromAave` Accounting, Freezing User ETH Withdrawals — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

An attacker can transfer aWETH directly to `LRTWithdrawalManager` before any ETH has been deposited through the contract's Aave integration. Because `totalETHDepositedToAave` is initialized to `0` and only updated via `_depositToAave`, the `_withdrawFromAave` function silently returns `0` when the actual aWETH balance exceeds the tracked principal. This causes `_processWithdrawalCompletion` to revert with `InsufficientLiquidityForWithdrawal`, freezing pending user ETH withdrawals.

---

### Finding Description

`LRTWithdrawalManager` maintains `totalETHDepositedToAave` as an accounting variable that tracks ETH deposited to Aave exclusively through `_depositToAave`. The `_withdrawFromAave` function caps the amount it will withdraw at `min(aaveBalance, totalETHDepositedToAave)`: [1](#0-0) 

When `totalETHDepositedToAave == 0` but `aaveAWETH.balanceOf(address(this)) > 0` (because an attacker transferred aWETH directly to the contract), the computation is:

```
withdrawablePrincipal = min(aaveBalance, 0) = 0
withdrawnAmount       = min(amountNeeded, 0) = 0
→ returns 0 silently (no revert)
```

`_processWithdrawalCompletion` then checks the ETH balance after the silent no-op withdrawal and reverts: [2](#0-1) 

The `totalETHDepositedToAave` variable is initialized to `0` and is only incremented inside `_depositToAave`: [3](#0-2) 

Because aWETH is a standard ERC-20 token, any address can transfer it directly to `LRTWithdrawalManager` without going through `_depositToAave`, leaving `totalETHDepositedToAave` at `0` while `aaveBalance > 0`. The contract address is deterministic (UUPS proxy), so the attacker can compute it before any Aave deposits are made.

---

### Impact Explanation

**Impact: Medium — Temporary freezing of user ETH withdrawal funds.**

All pending ETH withdrawal completions that require Aave liquidity (i.e., where `address(this).balance < request.expectedAssetAmount`) will revert with `InsufficientLiquidityForWithdrawal` for as long as the accounting mismatch persists. After an operator calls `collectInterestToTreasury()` to sweep the donated aWETH, `aaveBalance` drops to `0`, causing `_withdrawFromAave` to revert with `InsufficientAaveBalance` instead — the freeze continues until the operator either re-deposits ETH to Aave or disables the integration. [4](#0-3) 

---

### Likelihood Explanation

**Likelihood: Low.**

- The attacker must spend real aWETH (a liquid, valuable asset) with no direct financial gain; the donated aWETH is eventually swept to the protocol treasury.
- The attack window is widest when `totalETHDepositedToAave == 0`: immediately after Aave integration is configured/enabled, or after a full emergency withdrawal resets the counter to `0`.
- Operator intervention (`collectInterestToTreasury`, `depositIdleETHToAave`, or `setAaveIntegrationEnabled(false)`) resolves the freeze, so the DOS is temporary.

---

### Recommendation

When `configureAaveIntegration` or `setAaveIntegrationEnabled(true)` is called, initialize `totalETHDepositedToAave` to match any pre-existing aWETH balance held by the contract:

```solidity
// In configureAaveIntegration / setAaveIntegrationEnabled(true):
uint256 existingBalance = IAToken(aaveAWETH_).balanceOf(address(this));
if (existingBalance > 0) {
    totalETHDepositedToAave = existingBalance;
}
```

Alternatively, add a dedicated sweep function that transfers any aWETH received outside of `_depositToAave` to the treasury and resets the accounting, analogous to the recommendation in the reference report.

---

### Proof of Concept

1. Aave integration is configured and enabled; `totalETHDepositedToAave == 0` (no ETH deposited yet via `_depositToAave`).
2. Attacker calls `aaveAWETH.transfer(address(lrtWithdrawalManager), 1 ether)`.
3. `aaveAWETH.balanceOf(address(lrtWithdrawalManager)) == 1 ether`; `totalETHDepositedToAave == 0`.
4. A user calls `completeWithdrawal(ETH, ...)` for a request of `0.5 ether`; `address(lrtWithdrawalManager).balance == 0`.
5. `_processWithdrawalCompletion` enters the Aave branch: `contractBalance (0) < expectedAssetAmount (0.5 ether)`.
6. `_withdrawFromAave(0.5 ether)` computes `withdrawablePrincipal = min(1 ether, 0) = 0`, returns `0` silently.
7. `balanceAfter == 0 < 0.5 ether` → reverts `InsufficientLiquidityForWithdrawal`.
8. All ETH withdrawal completions are frozen until operator intervention. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L64-65)
```text
    bool public isAaveIntegrationEnabled;
    uint256 public totalETHDepositedToAave;
```

**File:** contracts/LRTWithdrawalManager.sol (L719-732)
```text
        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
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
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L894-901)
```text
    function _depositToAave(uint256 amount) internal {
        if (amount == 0) return;

        aaveWETHGateway.depositETH{ value: amount }(aavePool, address(this), 0);
        totalETHDepositedToAave += amount;

        emit ETHDepositedToAave(amount, totalETHDepositedToAave);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L905-921)
```text
    function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
        if (amount == 0) return 0;

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;

        emit ETHWithdrawnFromAave(withdrawnAmount, totalETHDepositedToAave);
    }
```
