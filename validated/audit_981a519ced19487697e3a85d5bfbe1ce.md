### Title
Non-Payable `PROTOCOL_TREASURY` Permanently Blocks Aave Reconfiguration and Yield Collection — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`_collectInterestToTreasury()` performs a bare ETH `call` to `PROTOCOL_TREASURY` and hard-reverts on failure. Because this function is called unconditionally inside `configureAaveIntegration`, `setAaveIntegrationEnabled(false)`, and `emergencyWithdrawFromAave`, a non-payable treasury address permanently blocks all three operations while interest is accrued, freezing both yield and the ability to migrate to a new Aave pool.

---

### Finding Description

`_collectInterestToTreasury()` withdraws accrued interest from Aave and forwards it to `PROTOCOL_TREASURY` via a low-level call: [1](#0-0) 

```solidity
aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));

address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
(bool sent,) = payable(treasury).call{ value: interestAmount }("");
if (!sent) revert TreasuryTransferFailed();
```

If `PROTOCOL_TREASURY` is a contract without a `receive()` / `fallback()` function (e.g., a governance timelock, a multisig that rejects ETH, or a contract that was upgraded to remove ETH acceptance), `sent` is `false` and the function reverts with `TreasuryTransferFailed`.

This internal function is called unconditionally in three places whenever `aaveBalance > principal`:

1. **`configureAaveIntegration`** — line 442 [2](#0-1) 
2. **`setAaveIntegrationEnabled(false)`** — line 490 [3](#0-2) 
3. **`emergencyWithdrawFromAave`** — line 558 [4](#0-3) 

All three revert entirely, leaving the Aave state unchanged. Crucially, in `configureAaveIntegration` the `_withdrawFromAave` call for the principal is placed **after** `_collectInterestToTreasury`, so the principal also remains locked: [5](#0-4) 

There is no alternative code path to withdraw from Aave without first successfully transferring interest to the treasury.

---

### Impact Explanation

- **Unclaimed yield is permanently frozen**: All Aave interest accrued since the last collection cannot be extracted.
- **Aave pool migration is blocked**: The protocol cannot move to a new Aave pool version (`configureAaveIntegration` always reverts).
- **Emergency withdrawal is blocked**: `emergencyWithdrawFromAave` also calls `_collectInterestToTreasury` first and reverts.
- **Principal is also at risk**: Because `_withdrawFromAave` is never reached, user withdrawal funds deposited to Aave are also inaccessible until the treasury address is updated.

The admin can mitigate by updating `PROTOCOL_TREASURY` to a payable address via `lrtConfig.setContract`, but until that governance action completes, all Aave operations are frozen.

Scoped impact: **Medium — Permanent freezing of unclaimed yield** (and temporary freezing of principal until treasury is updated).

---

### Likelihood Explanation

`PROTOCOL_TREASURY` is set by `DEFAULT_ADMIN_ROLE` via `lrtConfig.setContract`. There is no validation that the address can receive ETH: [6](#0-5) 

Protocol treasuries are commonly smart contracts (governance timelocks, multisigs, fee splitters) that may not implement `receive()`. This is a realistic operational scenario, not a theoretical one. No attacker action is required — the condition arises from normal protocol configuration.

---

### Recommendation

Replace the hard-revert pattern in `_collectInterestToTreasury` with a pull-payment or try/catch approach. If the treasury transfer fails, the withdrawn ETH should remain in the contract (or be tracked for later collection) rather than reverting the entire operation:

```solidity
(bool sent,) = payable(treasury).call{ value: interestAmount }("");
if (!sent) {
    // Keep ETH in contract; emit event for manual recovery
    emit TreasuryTransferFailed(interestAmount, treasury);
    // Do NOT revert — allow caller to proceed
}
```

Alternatively, decouple interest collection from pool migration: skip `_collectInterestToTreasury` in `configureAaveIntegration` and `setAaveIntegrationEnabled` if the treasury transfer would fail, and let operators collect interest separately.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// NonPayableTreasury: reverts on ETH receive
contract NonPayableTreasury {
    // No receive() or fallback() — any ETH send reverts
}

// Test (Foundry):
// 1. Deploy LRTWithdrawalManager with NonPayableTreasury as PROTOCOL_TREASURY
// 2. Configure Aave integration (aavePool, aaveWETHGateway, aaveAWETH, aaveDataProvider)
// 3. Deposit ETH to Aave via depositIdleETHToAave
// 4. Advance time so Aave accrues interest (aaveAWETH.balanceOf > totalETHDepositedToAave)
// 5. Call configureAaveIntegration(newPool, newGateway, newAWETH, newDataProvider)
// 6. Assert: call reverts with TreasuryTransferFailed
// 7. Assert: aaveAWETH.balanceOf(withdrawalManager) unchanged — interest and principal still locked
```

The revert path is:
`configureAaveIntegration` → `aaveBalance > 0` → `_collectInterestToTreasury()` → `aaveWETHGateway.withdrawETH(...)` (succeeds, ETH now in contract) → `payable(NonPayableTreasury).call{value}("")` → `sent = false` → `revert TreasuryTransferFailed` → entire transaction reverts, ETH returned to Aave accounting is inconsistent (the `withdrawETH` already executed but the outer tx reverts, so Aave state is also rolled back).

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L438-449)
```text
        if (address(aaveAWETH) != address(0) && address(aaveWETHGateway) != address(0) && aavePool != address(0)) {
            uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
            if (aaveBalance > 0) {
                // First collect any accrued interest to treasury
                _collectInterestToTreasury();

                // Then withdraw all remaining principal from old Aave pool
                aaveBalance = aaveAWETH.balanceOf(address(this));
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
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

**File:** contracts/LRTWithdrawalManager.sol (L954-958)
```text
        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));

        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        (bool sent,) = payable(treasury).call{ value: interestAmount }("");
        if (!sent) revert TreasuryTransferFailed();
```

**File:** contracts/LRTConfig.sol (L244-251)
```text
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
    }
```
