### Title
Broken Old Aave Gateway Permanently Blocks Pool Migration and Freezes Yield — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`configureAaveIntegration` unconditionally calls `_collectInterestToTreasury()` via the **old** gateway before updating addresses. If the old gateway's `withdrawETH` reverts (e.g., pool deprecated, paused, or decommissioned), every migration and exit path reverts with no bypass, permanently freezing both accrued yield and principal in the old pool.

---

### Finding Description

When `configureAaveIntegration` is called to migrate to a new Aave pool, the contract first attempts to drain the old pool: [1](#0-0) 

Step 1 is `_collectInterestToTreasury()`, which calls `withdrawETH` on the **old** gateway: [2](#0-1) 

If `aaveWETHGateway.withdrawETH` reverts (old pool deprecated/paused), the entire `configureAaveIntegration` call reverts and the state variables (`aavePool`, `aaveWETHGateway`, `aaveAWETH`) are never updated.

**Every other exit path has the same flaw — there is no escape hatch:**

| Function | Also calls `_collectInterestToTreasury()`? |
|---|---|
| `configureAaveIntegration` | Yes — line 442 |
| `setAaveIntegrationEnabled(false)` | Yes — line 490 |
| `emergencyWithdrawFromAave` | Yes — line 558 |
| `collectInterestToTreasury` (external) | Yes — line 544 | [3](#0-2) [4](#0-3) 

All four paths call `_collectInterestToTreasury()` before any state change, and `_collectInterestToTreasury()` calls the old gateway unconditionally when `aaveBalance > totalETHDepositedToAave`. There is no admin-callable function that skips interest collection and directly updates the Aave addresses.

---

### Impact Explanation

- **Accrued yield is permanently frozen** in the old Aave pool — it cannot be collected or migrated. This matches the scoped impact: *Medium. Permanent freezing of unclaimed yield*.
- **Principal is also permanently frozen** — `_withdrawFromAave` (line 447 and 560) also calls `aaveWETHGateway.withdrawETH` on the old gateway, so it reverts too. This additionally matches: *Critical. Permanent freezing of funds*.
- The protocol cannot re-enable or reconfigure Aave integration at all while the old gateway is broken.

---

### Likelihood Explanation

Aave regularly deprecates pool versions (e.g., v2 → v3 migration). A deprecated Aave pool can have its `withdrawETH` revert or become non-functional. This is a documented, real-world lifecycle event — not a theoretical edge case. Any protocol using Aave long-term will face pool migrations. The precondition (accrued interest + deprecated old pool) is realistic and has historical precedent.

---

### Recommendation

Separate the interest-collection step from the reconfiguration step. Specifically:

1. Add a `forceConfigureAaveIntegration` (or modify `configureAaveIntegration`) that **skips** `_collectInterestToTreasury()` when the old gateway is known to be broken, allowing the address update to proceed regardless.
2. Alternatively, wrap the `_collectInterestToTreasury()` call inside `configureAaveIntegration` in a `try/catch` so that a revert from the old gateway is tolerated and the migration proceeds (with the interest left as irrecoverable, or logged for manual recovery).
3. Similarly, `emergencyWithdrawFromAave` should not be gated behind a mandatory interest-collection step — it is an emergency function and should be able to withdraw principal even if interest collection fails.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Mock old gateway that always reverts on withdrawETH
contract BrokenGateway {
    function withdrawETH(address, uint256, address) external pure {
        revert("pool deprecated");
    }
    function depositETH(address, address, uint16) external payable {}
}

// Mock aWETH that reports a balance > principal (simulating accrued interest)
contract MockAWETH {
    function balanceOf(address) external pure returns (uint256) {
        return 1.1 ether; // principal was 1 ETH, 0.1 ETH interest accrued
    }
    function forceApprove(address, uint256) external returns (bool) { return true; }
}

// Test (pseudocode, run on a local fork):
// 1. Deploy LRTWithdrawalManager, configure with BrokenGateway + MockAWETH
// 2. Set totalETHDepositedToAave = 1 ether (principal)
// 3. Call configureAaveIntegration(newPool, newGateway, newAWETH, newDataProvider)
// 4. Assert: transaction reverts with "pool deprecated"
// 5. Assert: aaveWETHGateway still points to BrokenGateway (no migration occurred)
// 6. Call setAaveIntegrationEnabled(false) → also reverts
// 7. Call emergencyWithdrawFromAave(type(uint256).max) → also reverts
// Conclusion: no path exists to migrate or recover funds
```

The root cause is at: [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTWithdrawalManager.sol (L486-497)
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

**File:** contracts/LRTWithdrawalManager.sol (L945-954)
```text
    function _collectInterestToTreasury() internal returns (uint256 interestAmount) {
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        uint256 principal = totalETHDepositedToAave;

        // Return 0 if no interest or balance is less than principal (accounting for rounding)
        if (aaveBalance <= principal) return 0;

        interestAmount = aaveBalance - principal;

        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));
```
