### Title
Bundled Interest Collection in `emergencyWithdrawFromAave` Blocks Emergency Principal Withdrawal When Treasury Rejects ETH - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`emergencyWithdrawFromAave()` and `setAaveIntegrationEnabled(false)` both unconditionally call `_collectInterestToTreasury()` before withdrawing the principal from Aave. If the protocol treasury address is a contract that cannot receive ETH, the interest-forwarding step reverts with `TreasuryTransferFailed`, and the entire call reverts — permanently blocking emergency principal recovery and Aave integration shutdown through these code paths.

### Finding Description

`_collectInterestToTreasury()` performs two sequential actions:

1. Withdraws accrued interest from Aave via `aaveWETHGateway.withdrawETH(...)`.
2. Forwards that ETH to the treasury via a low-level `call`. [1](#0-0) 

If the treasury's `receive()` or fallback reverts (e.g., the treasury is a governance contract, a multisig with a complex fallback, or any contract without a payable receive), the `if (!sent) revert TreasuryTransferFailed()` guard causes the entire call to revert. [2](#0-1) 

This revert propagates into both callers:

**`emergencyWithdrawFromAave()`** — calls `_collectInterestToTreasury()` before `_withdrawFromAave(amount)`: [3](#0-2) 

**`setAaveIntegrationEnabled(false)`** — calls `_collectInterestToTreasury()` before `_withdrawFromAave(aaveBalance)`: [4](#0-3) 

In both cases, the interest collection (the "fee" step) is batched ahead of the critical principal-recovery step. If the fee step fails, the principal step never executes — an exact structural analog to the SeaportProxy pattern where batched fee transfer at the end of a non-atomic loop caused all orders to fail.

### Impact Explanation

When Aave is at risk and the PAUSER_ROLE calls `emergencyWithdrawFromAave()`, the call reverts if any interest has accrued and the treasury cannot receive ETH. The ETH principal deposited to Aave remains locked there with no alternative withdrawal path in the contract. Similarly, `setAaveIntegrationEnabled(false)` cannot complete, leaving the integration permanently enabled and the principal inaccessible through the intended shutdown flow.

Impact: **Temporary freezing of funds** (Medium). The ETH principal is not lost but cannot be recovered through the designated emergency or shutdown paths until the treasury address is changed — which itself requires a separate admin action that may not be possible under time pressure.

### Likelihood Explanation

The treasury address is resolved dynamically from `lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY)`. [5](#0-4) 

If the treasury is ever set to a smart contract without a `receive()` function (e.g., a governance timelock, a custom treasury contract, or a multisig with a gas-limited fallback), the condition is met. Interest accrues continuously once Aave integration is active, so `aaveBalance > principal` will be true in virtually all real-world scenarios after any meaningful time has passed, making the interest-forwarding branch always execute.

### Recommendation

Decouple interest collection from principal withdrawal. Do not require the treasury transfer to succeed as a prerequisite for emergency operations. Options:

1. **Separate the steps**: In `emergencyWithdrawFromAave()` and `setAaveIntegrationEnabled(false)`, skip `_collectInterestToTreasury()` entirely and let interest be collected independently via the standalone `collectInterestToTreasury()` call.
2. **Use a try/catch**: Wrap `_collectInterestToTreasury()` in a `try/catch` so that a treasury transfer failure is logged but does not block the principal withdrawal.
3. **Accumulate interest in storage**: Instead of pushing ETH to the treasury immediately, record the accrued interest in a storage variable and let the treasury pull it separately.

### Proof of Concept

1. Aave integration is enabled; ETH is deposited and interest accrues (`aaveBalance > totalETHDepositedToAave`).
2. Treasury is set to a contract address that reverts on ETH receipt.
3. An emergency occurs (e.g., Aave exploit risk). PAUSER_ROLE calls `emergencyWithdrawFromAave(type(uint256).max)`.
4. Inside the call: `_collectInterestToTreasury()` withdraws interest from Aave, then calls `payable(treasury).call{value: interestAmount}("")` — this returns `false`.
5. `if (!sent) revert TreasuryTransferFailed()` fires; the entire transaction reverts.
6. `_withdrawFromAave(amount)` is never reached; the ETH principal remains in Aave.
7. `setAaveIntegrationEnabled(false)` exhibits the identical failure for the same reason. [6](#0-5) [1](#0-0)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L945-961)
```text
    function _collectInterestToTreasury() internal returns (uint256 interestAmount) {
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        uint256 principal = totalETHDepositedToAave;

        // Return 0 if no interest or balance is less than principal (accounting for rounding)
        if (aaveBalance <= principal) return 0;

        interestAmount = aaveBalance - principal;

        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));

        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        (bool sent,) = payable(treasury).call{ value: interestAmount }("");
        if (!sent) revert TreasuryTransferFailed();

        emit InterestCollectedToTreasury(interestAmount, treasury);
    }
```
