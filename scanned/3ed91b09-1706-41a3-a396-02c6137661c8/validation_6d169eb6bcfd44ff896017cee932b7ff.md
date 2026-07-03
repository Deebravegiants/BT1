The code is clear. Let me verify the exact call chain and confirm there's no bypass path.

The call chain is fully confirmed. The vulnerability is real and traceable.

**Exact execution path:**

1. `emergencyWithdrawFromAave(amount)` — line 551, unconditionally calls `_collectInterestToTreasury()` at line 558 before any principal withdrawal.
2. `_collectInterestToTreasury()` — line 950: if `aaveBalance > principal`, proceeds; line 954: calls `aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this))` — succeeds, ETH lands in the contract; line 957: `payable(treasury).call{ value: interestAmount }("")` — fails if treasury is non-payable; line 958: `revert TreasuryTransferFailed` — entire transaction reverts, including the Aave withdrawal.
3. The revert unwinds everything. The interest remains as aWETH in Aave. `_withdrawFromAave(amount)` at line 560 is never reached.

There is no alternative emergency path. `setAaveIntegrationEnabled(false)` and `configureAaveIntegration()` both call `_collectInterestToTreasury()` under the same condition, so they are equally blocked. The only resolution is an admin changing `PROTOCOL_TREASURY` in `lrtConfig` to a payable address — but that is an out-of-band admin action, not a protocol-level escape hatch.

---

### Title
`emergencyWithdrawFromAave` permanently blocked by non-payable treasury when Aave interest has accrued — (`contracts/LRTWithdrawalManager.sol`)

### Summary
`emergencyWithdrawFromAave` unconditionally calls `_collectInterestToTreasury()` before withdrawing principal. If the `PROTOCOL_TREASURY` address is a non-payable contract and any interest has accrued, the treasury ETH transfer reverts, causing the entire emergency withdrawal to revert. The accrued yield is permanently frozen in Aave with no alternative recovery path.

### Finding Description
In `LRTWithdrawalManager.sol`, `emergencyWithdrawFromAave` is the sole role-gated emergency escape hatch for recovering ETH from Aave. [1](#0-0) 

It unconditionally calls `_collectInterestToTreasury()` before withdrawing principal: [2](#0-1) 

Inside `_collectInterestToTreasury()`, when `aaveBalance > totalETHDepositedToAave`, the function:
1. Withdraws the interest amount from Aave via `aaveWETHGateway.withdrawETH` (ETH arrives in the contract).
2. Attempts a raw ETH call to the treasury.
3. Reverts with `TreasuryTransferFailed` if the call fails. [3](#0-2) 

Because the entire transaction is atomic, the Aave withdrawal is also rolled back. The interest remains as aWETH in Aave, and `_withdrawFromAave(amount)` is never reached.

Every other code path that drains Aave also calls `_collectInterestToTreasury()` under the same condition: `setAaveIntegrationEnabled(false)` (line 490) and `configureAaveIntegration()` (line 442). All are equally blocked.

### Impact Explanation
Accrued Aave yield (aWETH interest above `totalETHDepositedToAave`) cannot be recovered by any on-chain path. The PAUSER_ROLE emergency function, the operator collection function, and the manager disable/reconfigure functions all revert. The yield is frozen in Aave until an admin changes `PROTOCOL_TREASURY` in `lrtConfig` to a payable address — an out-of-band fix that is not guaranteed and may itself be blocked by governance delays.

**Impact: Medium — Permanent freezing of unclaimed yield.**

### Likelihood Explanation
Many protocol treasury addresses are multisig wallets (e.g., Gnosis Safe) or governance contracts. Gnosis Safe proxies do have a `receive()` function, but other governance or timelock contracts commonly do not. The condition (non-payable treasury + any accrued interest) is realistic in production. No attacker action is required; the state arises naturally over time as Aave accrues interest.

### Recommendation
Decouple the interest collection from the emergency principal withdrawal. In `emergencyWithdrawFromAave`, skip the treasury transfer if it fails (or skip `_collectInterestToTreasury()` entirely), so the principal can always be recovered regardless of treasury state. For example:

```solidity
function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
    if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

    uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
    if (aaveBalance == 0) revert InsufficientAaveBalance();

    // Attempt interest collection but do NOT revert if treasury transfer fails
    try this._collectInterestToTreasuryExternal() {} catch {}

    uint256 withdrawnAmount = _withdrawFromAave(amount);
    emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
}
```

Alternatively, add a separate `emergencySkipInterest` flag or allow the PAUSER_ROLE to withdraw the full `aaveBalance` (principal + interest) directly to the contract, bypassing the treasury transfer entirely.

### Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

// Fork test (Foundry) demonstrating the block
contract NonPayableTreasury {
    // No receive() or fallback() — rejects ETH
}

contract PoCTest is Test {
    // Setup: deploy LRTWithdrawalManager with NonPayableTreasury as PROTOCOL_TREASURY
    // Deposit ETH to Aave, let time pass so aaveAWETH.balanceOf > totalETHDepositedToAave
    function test_emergencyWithdrawBlockedByNonPayableTreasury() public {
        // Preconditions:
        // isAaveIntegrationEnabled = true
        // aaveAWETH.balanceOf(withdrawalManager) > totalETHDepositedToAave (interest accrued)
        // lrtConfig.PROTOCOL_TREASURY = address(new NonPayableTreasury())

        uint256 aWETHBefore = aaveAWETH.balanceOf(address(withdrawalManager));

        vm.prank(pauserRole);
        vm.expectRevert(ILRTWithdrawalManager.TreasuryTransferFailed.selector);
        withdrawalManager.emergencyWithdrawFromAave(type(uint256).max);

        // Assert: aWETH balance unchanged — interest is frozen
        assertEq(aaveAWETH.balanceOf(address(withdrawalManager)), aWETHBefore);
    }
}
``` [4](#0-3)

### Citations

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
