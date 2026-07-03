### Title
ETH Withdrawals Depend on Aave WETH Pool Liquidity With No Fallback, Causing Temporary Fund Freeze - (File: contracts/LRTWithdrawalManager.sol)

### Summary

When the Aave integration is enabled in `LRTWithdrawalManager`, unlocked ETH is deposited into Aave's WETH pool. User calls to `completeWithdrawal` for ETH then depend on Aave's WETH pool having sufficient available liquidity to process the withdrawal. If Aave's WETH pool has high utilization (all WETH is borrowed), `aaveWETHGateway.withdrawETH()` will revert, causing `completeWithdrawal` to revert with no fallback path, temporarily freezing user funds.

### Finding Description

When `isAaveIntegrationEnabled` is `true`, the `unlockQueue` function deposits unlocked ETH into Aave via `_depositToAave`. Subsequently, when a user calls `completeWithdrawal(ETH_TOKEN, ...)`, the internal `_processWithdrawalCompletion` function checks whether the contract's ETH balance is sufficient. If not, it calls `_withdrawFromAave(amountNeeded)`:

```solidity
// LRTWithdrawalManager.sol lines 720-732
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);

        uint256 balanceAfter = address(this).balance;
        if (balanceAfter < request.expectedAssetAmount) {
            revert InsufficientLiquidityForWithdrawal();
        }
    }
}
```

Inside `_withdrawFromAave`, the call to `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))` is made with no try/catch and no fallback:

```solidity
// LRTWithdrawalManager.sol lines 905-921
function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
    ...
    aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
    totalETHDepositedToAave -= withdrawnAmount;
    ...
}
```

Aave's `withdrawETH` can revert when the WETH reserve's available liquidity is insufficient (i.e., utilization is at or near 100%). There is no alternative path for users to complete their ETH withdrawals in this scenario.

Critically, the admin recovery paths also fail under the same condition:
- `emergencyWithdrawFromAave` also calls `_withdrawFromAave` internally, so it too reverts if Aave's liquidity is insufficient.
- `setAaveIntegrationEnabled(false)` also calls `_withdrawFromAave` to drain the Aave balance before disabling, so it also reverts.

This means that when Aave's WETH pool has insufficient liquidity, **both user withdrawals and admin recovery are bricked simultaneously**, extending the freeze duration until Aave's liquidity recovers.

### Impact Explanation

**Temporary freezing of funds (Medium).** Users who have unlocked withdrawal requests for ETH cannot call `completeWithdrawal` successfully. Their rsETH has already been burned (in `unlockQueue`), and the ETH is locked in Aave. The freeze persists until Aave's WETH pool liquidity recovers. In extreme market conditions (e.g., a bank run on Aave), this could last for an extended period.

### Likelihood Explanation

Aave's WETH pool is one of the most liquid pools in DeFi, but during extreme market stress events (e.g., cascading liquidations, bank runs), utilization can spike to near 100%, making withdrawals temporarily impossible. The Aave integration is an opt-in feature enabled by the manager, so this only affects deployments where it has been enabled. Given that the protocol explicitly integrates with Aave for yield on queued ETH, this is a realistic operational scenario.

### Recommendation

Mirror the fix from H-07: check external protocol availability before committing to a single withdrawal path, and provide a fallback.

1. Before calling `_withdrawFromAave`, check Aave's available WETH liquidity (already exposed via `getAaveWithdrawableLiquidity()`). If insufficient, revert with a clear error rather than letting the Aave call revert opaquely.
2. Decouple the `setAaveIntegrationEnabled(false)` path from `_withdrawFromAave` so that the admin can disable Aave integration even when Aave's pool is illiquid (e.g., by skipping the withdrawal and leaving aWETH tokens in the contract to be claimed later separately).
3. Consider adding a separate `claimFromAave` function that can be called independently, so that `completeWithdrawal` can proceed using whatever ETH is already in the contract, and the Aave claim is a separate step.

### Proof of Concept

1. Manager enables Aave integration via `setAaveIntegrationEnabled(true)`.
2. Operator calls `unlockQueue(ETH_TOKEN, ...)` — this redeems ETH from `LRTUnstakingVault` and deposits it to Aave. `totalETHDepositedToAave` is now `X ETH`.
3. Aave's WETH pool utilization spikes to ~100% (e.g., due to a market event).
4. User calls `completeWithdrawal(ETH_TOKEN, referralId)`.
5. `_processWithdrawalCompletion` finds `address(this).balance < request.expectedAssetAmount` (ETH is in Aave, not in the contract).
6. `_withdrawFromAave(amountNeeded)` is called, which calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))`.
7. Aave reverts due to insufficient liquidity.
8. `completeWithdrawal` reverts — user's withdrawal is stuck.
9. Manager attempts `emergencyWithdrawFromAave` → also calls `_withdrawFromAave` → also reverts.
10. Manager attempts `setAaveIntegrationEnabled(false)` → also calls `_withdrawFromAave` → also reverts.
11. All ETH withdrawals remain frozen until Aave's WETH pool liquidity recovers. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L309-317)
```text
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

**File:** contracts/LRTWithdrawalManager.sol (L486-501)
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
