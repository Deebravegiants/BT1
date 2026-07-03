### Title
Reverting Treasury Blocks Disabling Aave Integration, Temporarily Freezing ETH - (`contracts/LRTWithdrawalManager.sol`)

### Summary

`setAaveIntegrationEnabled(false)` unconditionally calls `_collectInterestToTreasury()` before withdrawing principal. If the protocol treasury is a contract that reverts on ETH receive and any interest has accrued (`aaveAWETH.balanceOf > totalETHDepositedToAave`), the entire disable transaction reverts. Every escape hatch (`emergencyWithdrawFromAave`, `configureAaveIntegration`) follows the same code path and fails identically, leaving ETH locked in Aave with no in-contract recovery path.

### Finding Description

`setAaveIntegrationEnabled(false)` executes this sequence unconditionally when `aaveBalance > 0`:

```
setAaveIntegrationEnabled(false)          // LRTWithdrawalManager.sol:469
  └─ _collectInterestToTreasury()         // line 490
       ├─ aaveWETHGateway.withdrawETH(...)  // line 954  ← ETH leaves Aave
       └─ payable(treasury).call{value}("") // line 957
            └─ treasury reverts
                 └─ revert TreasuryTransferFailed()  // line 958
                      └─ entire tx reverts (ETH stays in Aave)
``` [1](#0-0) [2](#0-1) 

The treasury address is a runtime-configurable contract address fetched from `lrtConfig`. Protocol treasuries are commonly smart contracts (Gnosis Safe, DAO vaults, custom receivers). Any such contract lacking a `receive()` function, or whose fallback reverts, triggers this path. No admin compromise is required — this is a design flaw in the push-payment pattern used inside a critical control function.

All three functions that can withdraw from Aave share the same blocking dependency:

| Function | Caller | Also calls `_collectInterestToTreasury()`? |
|---|---|---|
| `setAaveIntegrationEnabled(false)` | LRT Manager | Yes — line 490 |
| `emergencyWithdrawFromAave` | PAUSER_ROLE | Yes — line 558 |
| `configureAaveIntegration` | LRT Manager | Yes — line 442 | [3](#0-2) [4](#0-3) 

There is no code path that withdraws ETH from Aave without first attempting to push interest to the treasury.

### Impact Explanation

**Medium — Temporary freezing of funds.**

ETH deposited to Aave via `_depositToAave` cannot be retrieved while the treasury reverts. User withdrawal requests for ETH that have been unlocked and deposited to Aave cannot be fulfilled. The freeze persists until the protocol admin updates the treasury address in `lrtConfig` to a valid ETH-accepting address and retries. The impact is not classified as permanent because the admin retains the ability to change the treasury address as a recovery path. It is not classified as "protocol insolvency" because the ETH is not lost — it remains in the Aave pool under the contract's aWETH balance.

### Likelihood Explanation

**Low-to-Medium.** The treasury address is set by the protocol admin and is expected to be a valid ETH receiver. However:
- Many production treasuries are smart contracts (multisigs, DAO vaults) that may not have a `receive()` function
- A treasury contract upgrade that removes ETH acceptance would silently create this condition
- Interest accrues continuously once the Aave integration is active, so the blocking condition (`aaveBalance > principal`) is always eventually true
- The bug requires no attacker — it is triggered by normal operational state

### Recommendation

Decouple interest collection from the disable/emergency path. Two options:

1. **Accumulate, don't push**: In `_collectInterestToTreasury`, withdraw interest from Aave into the contract and record it in a `pendingTreasuryBalance` variable. Allow the treasury to pull it separately. The disable path proceeds regardless of whether the treasury transfer succeeds.

2. **Wrap the treasury transfer in try/catch**: Withdraw interest from Aave to the contract, attempt the treasury transfer, and if it fails, leave the ETH in the contract (emitting an event). The disable operation completes regardless.

```solidity
// Option 2 sketch
aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));
(bool sent,) = payable(treasury).call{ value: interestAmount }("");
if (!sent) {
    // ETH stays in contract; emit event for off-chain monitoring
    emit TreasuryTransferFailed(interestAmount, treasury);
} else {
    emit InterestCollectedToTreasury(interestAmount, treasury);
}
```

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

import "forge-std/Test.sol";
import "../contracts/LRTWithdrawalManager.sol";

contract RevertingTreasury {
    // No receive() — any ETH push reverts
    fallback() external payable { revert("no ETH"); }
}

contract AaveDisableBlockedTest is Test {
    // Deploy LRTWithdrawalManager with mocked Aave (aaveBalance > totalETHDepositedToAave)
    // Set lrtConfig.PROTOCOL_TREASURY = address(new RevertingTreasury())
    // Call setAaveIntegrationEnabled(false) as LRT manager
    // Assert: tx reverts with TreasuryTransferFailed
    // Assert: isAaveIntegrationEnabled is still true
    // Assert: emergencyWithdrawFromAave also reverts
    function testDisableBlockedByRevertingTreasury() public {
        // ... setup omitted for brevity ...
        vm.expectRevert(LRTWithdrawalManager.TreasuryTransferFailed.selector);
        withdrawalManager.setAaveIntegrationEnabled(false);
        assertTrue(withdrawalManager.isAaveIntegrationEnabled());
    }
}
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L437-453)
```text
        // If reconfiguring an existing Aave integration, collect interest and withdraw all funds first
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

            // Revoke approval for old aWETH token
            IERC20(address(aaveAWETH)).forceApprove(address(aaveWETHGateway), 0);
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
