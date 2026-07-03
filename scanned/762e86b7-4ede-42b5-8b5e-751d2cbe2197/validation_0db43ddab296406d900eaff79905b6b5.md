### Title
ETH Withdrawal Completion Permanently Blocked by Aave High Utilization - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager._processWithdrawalCompletion` calls `_withdrawFromAave` without checking whether Aave's underlying WETH pool has sufficient liquidity. If Aave's WETH utilization is high, `aaveWETHGateway.withdrawETH` reverts, causing every ETH `completeWithdrawal` call to revert and temporarily freezing all unlocked user ETH withdrawals.

### Finding Description

When the Aave integration is enabled, `_processWithdrawalCompletion` (the internal function backing both `completeWithdrawal` and `completeWithdrawalForUser`) attempts to pull ETH from Aave whenever the contract's idle ETH balance is insufficient to cover a user's unlocked request:

```solidity
// LRTWithdrawalManager.sol L720-731
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);          // <-- no try/catch

        uint256 balanceAfter = address(this).balance;
        if (balanceAfter < request.expectedAssetAmount) {
            revert InsufficientLiquidityForWithdrawal();
        }
    }
}
```

`_withdrawFromAave` caps the withdrawal at the principal balance but unconditionally calls the external gateway:

```solidity
// LRTWithdrawalManager.sol L917
aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
```

Aave's `withdrawETH` reverts when the pool's available WETH liquidity (i.e., total supplied WETH minus borrowed WETH) is less than `withdrawnAmount`. This is a well-known property of peer-to-peer lending protocols: suppliers cannot withdraw tokens that have been lent out to borrowers. The contract even exposes a view function `getAaveWithdrawableLiquidity()` that reads the underlying WETH balance of the aWETH contract, confirming the team is aware of this constraint, yet the withdrawal path does not consult it.

The deposit path in `unlockQueue` correctly wraps the Aave interaction in a try/catch:

```solidity
// LRTWithdrawalManager.sol L311-316
try this.depositToAaveExternal(assetAmountUnlocked) { }
catch (bytes memory reason) {
    emit AaveDepositFailed(assetAmountUnlocked, reason);
    // Silently fail if Aave deposit fails (e.g., pool at max capacity)
}
```

No equivalent protection exists on the withdrawal side.

### Impact Explanation

**Medium — Temporary freezing of funds.**

When Aave's WETH utilization is high (a realistic condition during market stress, liquidation cascades, or high borrow demand), every call to `completeWithdrawal(ETH_TOKEN, ...)` and `completeWithdrawalForUser(ETH_TOKEN, ...)` reverts. All users who have already waited through the withdrawal delay and whose requests have been unlocked are unable to receive their ETH. The freeze persists until Aave's utilization drops below the threshold that allows the required withdrawal amount, which is outside the protocol's control.

### Likelihood Explanation

Aave WETH pools regularly experience elevated utilization during periods of market volatility. The protocol actively deposits idle ETH into Aave (`depositIdleETHToAave`, `unlockQueue` auto-deposit), meaning a significant fraction of the withdrawal manager's ETH may be in Aave at any given time. If the idle contract balance is zero and Aave utilization is high, every ETH withdrawal completion fails. This is a realistic, non-exotic market condition.

### Recommendation

Mirror the pattern already used for Aave deposits: wrap the `_withdrawFromAave` call in a try/catch inside `_processWithdrawalCompletion`. If the Aave withdrawal fails, revert with a descriptive error so the user knows to retry later, or — better — check `getAaveWithdrawableLiquidity()` before attempting the withdrawal and revert early with `InsufficientLiquidityForWithdrawal` without making the external call. Additionally, consider allowing partial Aave withdrawals combined with idle contract balance to satisfy requests when full Aave liquidity is unavailable.

### Proof of Concept

1. Operator calls `unlockQueue(ETH_TOKEN, ...)` — this redeems ETH from the unstaking vault and auto-deposits it into Aave via `depositToAaveExternal`. The contract's idle ETH balance is now 0; all ETH sits in Aave as aWETH.
2. Aave's WETH pool reaches high utilization (e.g., 95%+) due to external borrowers.
3. Alice calls `completeWithdrawal(ETH_TOKEN, "ref")`. Her request is unlocked and the delay has passed.
4. Inside `_processWithdrawalCompletion`: `address(this).balance == 0 < request.expectedAssetAmount`, so `_withdrawFromAave(amountNeeded)` is called.
5. `_withdrawFromAave` computes `withdrawnAmount = amountNeeded` (within principal), then calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))`.
6. Aave reverts because available WETH liquidity < `withdrawnAmount`.
7. The entire transaction reverts. Alice's withdrawal request is not consumed (state rolls back). She cannot complete her withdrawal.
8. Every other ETH withdrawal caller faces the same revert until Aave utilization drops. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L309-316)
```text
        // If Aave integration is enabled and asset is ETH, deposit to Aave
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L681-689)
```text
    /// @notice Get withdrawable liquidity available in Aave
    /// @return withdrawableLiquidity The amount of WETH that can be withdrawn from Aave
    /// @dev This is the underlying WETH balance in the aWETH contract
    function getAaveWithdrawableLiquidity() external view returns (uint256 withdrawableLiquidity) {
        if (address(aaveAWETH) == address(0)) return 0;

        // The withdrawable liquidity is the WETH balance of the aWETH contract
        return IERC20(WETH_ADDRESS).balanceOf(address(aaveAWETH));
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L719-731)
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
