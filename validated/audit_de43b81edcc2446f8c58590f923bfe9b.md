### Title
`emergencyWithdrawFromAave` Permanently Blocked by Reverting `PROTOCOL_TREASURY` When Interest Has Accrued - (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`emergencyWithdrawFromAave` unconditionally calls `_collectInterestToTreasury()` before withdrawing principal. If `PROTOCOL_TREASURY` is a contract that reverts on ETH receive and any interest has accrued in Aave, the emergency path always reverts — leaving all ETH permanently locked in Aave with no callable recovery function.

---

### Finding Description

`emergencyWithdrawFromAave` is the sole privileged emergency escape hatch for ETH deposited to Aave. Its implementation is: [1](#0-0) 

Before withdrawing any principal, it unconditionally calls `_collectInterestToTreasury()` at line 558. That internal function:

1. Computes `interestAmount = aaveBalance - principal` (line 952)
2. Calls `aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this))` (line 954)
3. Attempts `payable(treasury).call{ value: interestAmount }("")` (line 957)
4. **Reverts with `TreasuryTransferFailed` if the call returns false** (line 958) [2](#0-1) 

Because the entire transaction reverts, the `withdrawETH` at line 954 is also rolled back — all ETH remains in Aave.

There is no alternative recovery path:
- `setAaveIntegrationEnabled(false)` also calls `_collectInterestToTreasury()` first (line 490), same failure.
- `configureAaveIntegration` also calls `_collectInterestToTreasury()` first (line 442), same failure.
- `collectInterestToTreasury()` (external) also routes through `_collectInterestToTreasury()`. [3](#0-2) 

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

Once `PROTOCOL_TREASURY` cannot receive ETH (e.g., a multisig contract that was upgraded, a DAO treasury with a broken `receive()`, or any contract without a payable fallback), and at least 1 wei of Aave interest has accrued, every function that could recover the principal from Aave reverts. The ETH deposited to Aave by the `LRTWithdrawalManager` is permanently inaccessible.

---

### Likelihood Explanation

**Medium.** `PROTOCOL_TREASURY` is a configurable contract address. Smart-contract treasuries (multisigs, DAO vaults) are common and can lose the ability to receive raw ETH through upgrades, self-destruct, or misconfiguration. Aave interest accrues continuously from the first block after deposit, so the precondition `aaveBalance > totalETHDepositedToAave` is satisfied almost immediately after any deposit. The combination is realistic and requires no privileged collusion — only a treasury contract that cannot accept ETH.

---

### Recommendation

Decouple interest collection from the emergency withdrawal path. Two options:

1. **Skip interest collection in `emergencyWithdrawFromAave`** — remove the `_collectInterestToTreasury()` call entirely from the emergency path. The PAUSER_ROLE can collect interest separately once the emergency is resolved.

2. **Use try/catch or suppress the revert** — wrap the treasury transfer in `_collectInterestToTreasury` with a `try/catch` or check-and-continue pattern so that a failed treasury transfer does not block the principal withdrawal.

Option 1 is simpler and more robust for an emergency function.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

// Fork test (local fork or Anvil fork of mainnet)
// 1. Deploy a mock treasury that reverts on receive:
contract RevertingTreasury {
    receive() external payable { revert("no ETH"); }
}

// 2. Set PROTOCOL_TREASURY to RevertingTreasury in lrtConfig.

// 3. Deposit ETH to Aave via LRTWithdrawalManager (isAaveIntegrationEnabled = true).

// 4. Advance 1+ blocks so Aave accrues ≥1 wei of interest
//    (aaveAWETH.balanceOf(withdrawalManager) > totalETHDepositedToAave).

// 5. Call as PAUSER_ROLE:
//    withdrawalManager.emergencyWithdrawFromAave(type(uint256).max);
//    → reverts with TreasuryTransferFailed
//    → all ETH remains locked in Aave

// 6. Assert: no alternative function can recover the ETH.
//    setAaveIntegrationEnabled(false) → same revert
//    configureAaveIntegration(...)    → same revert
```

The revert at [4](#0-3)  propagates up through `emergencyWithdrawFromAave` at [5](#0-4) , blocking the principal withdrawal at line 560 entirely.

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L945-958)
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
```
