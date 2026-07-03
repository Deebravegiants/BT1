Audit Report

## Title
Residual `totalETHDepositedToAave` After Full Withdrawal Permanently Breaks Aave Accounting, Temporarily Freezing ETH Withdrawal Completions — (`contracts/LRTWithdrawalManager.sol`)

## Summary

When Aave's aToken balance rounds down by 1–2 wei (a condition explicitly tolerated by `_checkAaveHealth`), a full withdrawal of the Aave position leaves `totalETHDepositedToAave` with a non-zero residual (e.g., 1) while `aaveAWETH.balanceOf(address(this))` reaches zero. Every subsequent call to `_withdrawFromAave` then hits the `aaveBalance == 0` guard and reverts with `InsufficientAaveBalance`, blocking all ETH withdrawal completions that require Aave liquidity until an admin manually disables the integration.

## Finding Description

`_checkAaveHealth` explicitly permits up to 2 wei of divergence between `aaveAWETH.balanceOf(address(this))` and `totalETHDepositedToAave`: [1](#0-0) 

`_withdrawFromAave` computes the withdrawable amount as `min(aaveBalance, totalETHDepositedToAave)` and then subtracts only the withdrawn amount from `totalETHDepositedToAave`: [2](#0-1) 

When `aaveBalance = N - 1` and `totalETHDepositedToAave = N` (a 1-wei rounding difference within the tolerated range):

| Step | Value |
|---|---|
| `withdrawablePrincipal` | `min(N-1, N) = N-1` |
| `withdrawnAmount` | `min(amount, N-1) = N-1` (for full withdrawal) |
| aWETH burned by gateway | `N-1` → `aaveBalance = 0` |
| `totalETHDepositedToAave -= N-1` | **residual = 1** |

After this call, `aaveBalance == 0` but `totalETHDepositedToAave == 1`. Any subsequent `_withdrawFromAave` call hits the guard at line 909 and reverts: [3](#0-2) 

There is no code path that can reset `totalETHDepositedToAave` to zero without a contract upgrade or admin disabling the integration, because every write goes through `_depositToAave` (increments) or `_withdrawFromAave` (decrements, but that now reverts at line 909).

## Impact Explanation

`completeWithdrawal` calls `_withdrawFromAave` whenever the contract's ETH balance is insufficient to cover a pending ETH withdrawal request and Aave integration is enabled: [4](#0-3) 

Once the residual state is reached, every such call reverts with `InsufficientAaveBalance`, blocking all ETH withdrawal completions that require Aave liquidity. This constitutes **Temporary freezing of funds (Medium)**: the freeze persists until the LRT Manager calls `setAaveIntegrationEnabled(false)`, but the accounting corruption (`totalETHDepositedToAave > 0` with zero aWETH) is permanent without an upgrade.

## Likelihood Explanation

Aave v3 aToken balances are known to round down by 1 wei due to ray-precision interest index arithmetic. The contract's own `_checkAaveHealth` explicitly documents and tolerates this (up to 2 wei). The precondition is therefore a normal operating condition, not an edge case. Any full withdrawal of the Aave position after even a single block of interest accrual can trigger this. No attacker action is required — normal protocol operation (users completing ETH withdrawals that drain the Aave position) is sufficient.

## Recommendation

When `withdrawnAmount >= aaveBalance` (i.e., the entire aWETH balance is being withdrawn), zero out `totalETHDepositedToAave` unconditionally rather than subtracting:

```solidity
if (withdrawnAmount >= aaveBalance) {
    totalETHDepositedToAave = 0;
} else {
    totalETHDepositedToAave -= withdrawnAmount;
}
```

This ensures that draining all aWETH always resets the principal tracker to zero, regardless of sub-wei rounding.

## Proof of Concept

Foundry fork test sequence against Aave v3 mainnet:

1. Call `_depositToAave(100 ether)` → `totalETHDepositedToAave = 100e18`.
2. Advance 1 block so Aave interest accrues; `aaveAWETH.balanceOf(withdrawalManager)` becomes `100e18 - 1` due to ray-precision rounding.
3. Trigger `completeWithdrawal` for a request of `100 ether` with zero contract ETH balance → calls `_withdrawFromAave(100e18)`.
4. Inside `_withdrawFromAave`: `withdrawablePrincipal = 100e18 - 1`, `withdrawnAmount = 100e18 - 1`, gateway burns all aWETH → `aaveBalance = 0`, `totalETHDepositedToAave = 1`.
5. Assert: `aaveAWETH.balanceOf(withdrawalManager) == 0` ✓
6. Assert: `totalETHDepositedToAave == 1` ← bug
7. Call `completeWithdrawal` for any subsequent ETH request with insufficient contract balance → `_withdrawFromAave` reverts at line 909 with `InsufficientAaveBalance` ← freeze confirmed.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L720-724)
```text
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);
```

**File:** contracts/LRTWithdrawalManager.sol (L908-909)
```text
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();
```

**File:** contracts/LRTWithdrawalManager.sol (L912-918)
```text
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L929-931)
```text
        // Allow small rounding differences (up to 2 wei)
        // Check if balance is significantly less than principal
        if (principal > aaveBalance && principal - aaveBalance > 2) return false;
```
