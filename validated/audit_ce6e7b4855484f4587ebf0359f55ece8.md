### Title
Aave WETH Liquidity Exhaustion Blocks All ETH Withdrawals With No Functional Escape Hatch — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

When `isAaveIntegrationEnabled` is `true` and the Aave WETH pool reaches 100% utilization, every `completeWithdrawal` call for ETH reverts. Critically, every admin escape hatch (`emergencyWithdrawFromAave`, `setAaveIntegrationEnabled(false)`, `configureAaveIntegration`) also calls `_withdrawFromAave` internally and reverts under the same condition, leaving the protocol with no on-chain path to unblock user withdrawals.

---

### Finding Description

`_processWithdrawalCompletion` contains the following block:

```solidity
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);   // ← no try/catch
        ...
    }
}
``` [1](#0-0) 

`_withdrawFromAave` calls the Aave gateway with no error handling:

```solidity
aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
``` [2](#0-1) 

When Aave WETH utilization is at 100%, `withdrawETH` reverts (Aave error `35` — `UNDERLYING_BALANCE_ZERO`). Because there is no `try/catch`, the revert propagates through `_processWithdrawalCompletion` → `completeWithdrawal`, blocking every ETH withdrawal.

**All three admin escape hatches are equally broken:**

| Function | Why it also reverts |
|---|---|
| `emergencyWithdrawFromAave` | Calls `_withdrawFromAave(amount)` directly (line 560) |
| `setAaveIntegrationEnabled(false)` | Calls `_withdrawFromAave(aaveBalance)` before setting the flag (lines 494–495) |
| `configureAaveIntegration` (reconfigure) | Calls `_withdrawFromAave(aaveBalance)` before updating addresses (line 447) | [3](#0-2) [4](#0-3) 

Because the entire transaction reverts, the `popFront()` and `delete withdrawalRequests[requestId]` executed earlier in `_processWithdrawalCompletion` are also rolled back, so user requests are not lost — but they cannot be fulfilled until Aave liquidity recovers.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

All ETH withdrawal completions are blocked for the duration of Aave WETH pool illiquidity. The protocol has no functional on-chain mechanism to override this: the emergency withdrawal, the integration disable path, and the reconfiguration path all share the same broken `_withdrawFromAave` call. The only resolution is either Aave liquidity recovering organically or a contract upgrade via governance.

The "permanent" framing in the question is overstated — Aave WETH at 100% utilization is a temporary market condition on mainnet — so this does not meet the Critical "permanent freezing" bar. It is a concrete, prolonged temporary freeze with no admin override.

---

### Likelihood Explanation

Aave v3 WETH on mainnet has historically reached very high utilization during periods of high ETH borrowing demand (e.g., around Merge, liquid staking yield spikes). While sustained 100% utilization is uncommon, it is a realistic market condition. The protocol actively deposits idle ETH into Aave, so any non-trivial Aave balance combined with a high-utilization event triggers this path.

---

### Recommendation

Wrap the `_withdrawFromAave` call inside `_processWithdrawalCompletion` in a `try/catch` and fall back gracefully (e.g., revert with a clear `InsufficientLiquidityForWithdrawal` error rather than an opaque Aave revert). More importantly, add a force-disable path in `setAaveIntegrationEnabled(false)` that sets `isAaveIntegrationEnabled = false` **unconditionally** and only attempts the Aave withdrawal as a best-effort (try/catch), so the integration can always be disabled regardless of Aave pool state. This unblocks `completeWithdrawal` immediately since the Aave branch is only entered when `isAaveIntegrationEnabled == true`. [5](#0-4) 

---

### Proof of Concept

```solidity
// Fork mainnet, set Aave WETH utilization to ~100% by borrowing all available WETH
// Then:
vm.prank(user);
withdrawalManager.completeWithdrawal(ETH_TOKEN, "ref");
// → reverts with Aave error (UNDERLYING_BALANCE_ZERO or similar)

// Attempt admin escape:
vm.prank(manager);
withdrawalManager.setAaveIntegrationEnabled(false);
// → also reverts (calls _withdrawFromAave internally)

vm.prank(pauser);
withdrawalManager.emergencyWithdrawFromAave(type(uint256).max);
// → also reverts (calls _withdrawFromAave internally)

// No on-chain path exists to unblock withdrawals
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L486-503)
```text
        if (!enabled) {
            uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
            if (aaveBalance > 0) {
                // First collect any accrued interest to treasury
                _collectInterestToTreasury();

                // Then withdraw remaining principal from Aave back to contract
                aaveBalance = aaveAWETH.balanceOf(address(this));
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
                }
            }

            // Revoke approval for aWETH token to Aave WETH Gateway
            _revokeApprovalToAaveWETHGateway();
        }

        isAaveIntegrationEnabled = enabled;
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

**File:** contracts/LRTWithdrawalManager.sol (L917-917)
```text
        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
```
