### Title
ETH Withdrawal Completion Blocked by Aave Pool Liquidity Shortage - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

When the Aave integration is active, `completeWithdrawal` for ETH depends on successfully pulling ETH back from Aave's WETH pool via `aaveWETHGateway.withdrawETH`. If Aave's WETH pool has insufficient available liquidity (utilization near 100%), this call reverts, causing the entire `completeWithdrawal` transaction to revert and temporarily freezing users' unlocked ETH withdrawal requests.

---

### Finding Description

`LRTWithdrawalManager` optionally deposits idle ETH into Aave v3 to earn yield. During `unlockQueue`, after pulling ETH from `LRTUnstakingVault`, the contract attempts to deposit it into Aave: [1](#0-0) 

When a user later calls `completeWithdrawal`, `_processWithdrawalCompletion` checks whether the contract's direct ETH balance covers the request. If not (the normal case when Aave integration is active, since most ETH has been deposited there), it calls `_withdrawFromAave`: [2](#0-1) 

`_withdrawFromAave` unconditionally calls `aaveWETHGateway.withdrawETH`: [3](#0-2) 

`IWrappedTokenGatewayV3.withdrawETH` is a thin wrapper that calls Aave's pool `withdraw`. Aave's pool reverts when available liquidity (total supplied minus total borrowed) is less than the requested withdrawal amount — a well-known condition when utilization approaches 100%. [4](#0-3) 

Because the revert propagates up through `_processWithdrawalCompletion`, the entire `completeWithdrawal` call reverts. The user's withdrawal request is preserved (state is rolled back), but they are unable to complete it for as long as Aave's WETH pool remains illiquid.

---

### Impact Explanation

**Temporary freezing of funds (Medium).** Users who have already had their ETH withdrawal requests unlocked — meaning their rsETH has been burned and the ETH has been allocated — cannot receive their ETH while Aave's WETH pool is illiquid. The funds are not permanently lost, but they are inaccessible for an indefinite period. The `emergencyWithdrawFromAave` function exists but is gated to `PAUSER_ROLE` and itself calls `_withdrawFromAave`, which would also revert under the same liquidity shortage. [5](#0-4) 

---

### Likelihood Explanation

**Realistic.** Aave WETH utilization reaching near 100% is a documented market-stress scenario (e.g., during ETH price crashes when borrowers rush to borrow WETH). Additionally, an attacker with sufficient capital can deliberately borrow WETH from Aave to drain available liquidity, blocking all pending LRT-rsETH ETH withdrawals. This mirrors the Morpho analog exactly: an attacker borrows the entire pool amount to prevent withdrawals. The capital requirement is high but not prohibitive for a motivated attacker targeting a large protocol.

---

### Recommendation

1. **Partial-fill fallback**: If `aaveWETHGateway.withdrawETH` reverts or returns less than needed, allow the user to receive whatever ETH is directly available in the contract and record the shortfall for a later retry, rather than reverting the entire completion.
2. **Try/catch on Aave withdrawal**: Wrap `_withdrawFromAave` in a `try/catch` inside `_processWithdrawalCompletion` (similar to how `depositToAaveExternal` is wrapped in `unlockQueue`), and revert with a clearer user-facing error only after the catch, preserving the request state.
3. **Aave liquidity pre-check**: Before depositing ETH into Aave during `unlockQueue`, verify that the pool's available liquidity is sufficient to cover pending unlocked withdrawals, and keep a reserve in the contract.

---

### Proof of Concept

1. Aave integration is enabled; operator calls `unlockQueue(ETH_TOKEN, ...)` — ETH is pulled from `LRTUnstakingVault` and deposited into Aave via `depositToAaveExternal`. [6](#0-5) 
2. User's ETH withdrawal request is now unlocked (`nextLockedNonce` advanced past their nonce).
3. Aave WETH pool utilization reaches ~100% (organically or via an attacker borrowing WETH from Aave).
4. User calls `completeWithdrawal(ETH_TOKEN, referralId)`.
5. `_processWithdrawalCompletion` runs: `contractBalance` (near zero, since ETH is in Aave) `< request.expectedAssetAmount`. [7](#0-6) 
6. `_withdrawFromAave(amountNeeded)` calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))`. [8](#0-7) 
7. Aave pool reverts: insufficient available WETH liquidity.
8. Entire `completeWithdrawal` transaction reverts.
9. User's ETH is locked in Aave, inaccessible until pool liquidity recovers or an admin manually intervenes — but `emergencyWithdrawFromAave` also calls `_withdrawFromAave` and would revert under the same condition. [9](#0-8)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L306-317)
```text
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);

        // If Aave integration is enabled and asset is ETH, deposit to Aave
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L551-563)
```text
    function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

        uint256 withdrawnAmount = _withdrawFromAave(amount);

        emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
    }
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

**File:** contracts/interfaces/aave/IWrappedTokenGatewayV3.sol (L4-8)
```text
interface IWrappedTokenGatewayV3 {
    function depositETH(address pool, address onBehalfOf, uint16 referralCode) external payable;

    function withdrawETH(address pool, uint256 amount, address to) external;
}
```
