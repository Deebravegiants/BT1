### Title
Emergency Withdrawal Path Blocked by Reverting Treasury — (`contracts/LRTWithdrawalManager.sol`)

### Summary

`emergencyWithdrawFromAave` unconditionally calls `_collectInterestToTreasury()` before withdrawing principal. If the treasury address is a contract that reverts on ETH receipt and interest has accrued, the entire emergency call reverts, preventing `PAUSER_ROLE` from recovering user ETH from Aave.

### Finding Description

`emergencyWithdrawFromAave` is the sole privileged path for `PAUSER_ROLE` to pull ETH out of Aave in an emergency: [1](#0-0) 

Line 558 calls `_collectInterestToTreasury()` unconditionally — before any principal is withdrawn. Inside that function: [2](#0-1) 

The sequence is:
1. Compute `interestAmount = aaveBalance - totalETHDepositedToAave`
2. Call `aaveWETHGateway.withdrawETH(...)` — ETH is now in the contract
3. Call `payable(treasury).call{ value: interestAmount }("")`
4. **If `!sent`, revert `TreasuryTransferFailed()`** — rolling back the entire transaction

The treasury address is resolved at call time from `lrtConfig`: [3](#0-2) 

If the treasury is a smart contract (multisig, DAO vault, or any contract without a `receive()` function), the ETH push will revert. Because `_collectInterestToTreasury()` is called unconditionally and its failure propagates up, `emergencyWithdrawFromAave` always reverts when `aaveBalance > totalETHDepositedToAave` and the treasury cannot accept ETH. There is no alternative code path in the contract for `PAUSER_ROLE` to recover principal without going through this function.

### Impact Explanation

User ETH deposited to Aave via the withdrawal manager is frozen for as long as the treasury remains non-receivable. The `PAUSER_ROLE` — the role specifically designed for emergency action — is rendered ineffective. Recovery requires admin intervention to update the treasury address in `LRTConfig`, which may not be possible during the same emergency that triggered the need for `emergencyWithdrawFromAave`. This constitutes at minimum **temporary freezing of funds** and escalates to **permanent freezing** if admin keys are unavailable during the emergency.

### Likelihood Explanation

Protocol treasuries are frequently smart contracts (Gnosis Safe, DAO treasury, custom vaults). Any such contract that lacks a `receive()` function, has a reverting fallback, or is paused/upgraded will trigger this path. Interest accrues automatically in Aave over time, so `aaveBalance > totalETHDepositedToAave` is the normal operating state after any non-trivial period. No attacker action is required — the condition arises from normal protocol operation combined with a realistic treasury configuration.

### Recommendation

Decouple interest collection from the emergency withdrawal path. Two options:

1. **Skip interest collection on failure**: Wrap the treasury transfer in a try/catch or check `sent` without reverting — log the failure and continue to withdraw principal.
2. **Remove interest collection from the emergency path entirely**: Let `emergencyWithdrawFromAave` withdraw the full `aaveBalance` (principal + interest) to the contract, and handle treasury distribution separately via `collectInterestToTreasury()`.

### Proof of Concept

```solidity
// Fork test (local/private testnet)
// 1. Deploy a RevertingTreasury contract with no receive() function
// 2. Set lrtConfig PROTOCOL_TREASURY to RevertingTreasury
// 3. Enable Aave integration, deposit ETH, advance time so interest accrues
//    (aaveAWETH.balanceOf(withdrawalManager) > totalETHDepositedToAave)
// 4. As PAUSER_ROLE, call emergencyWithdrawFromAave(type(uint256).max)
// 5. Assert: call reverts with TreasuryTransferFailed
// 6. Assert: aaveAWETH.balanceOf(withdrawalManager) is unchanged (principal still locked)
// 7. Assert: no other function exists for PAUSER_ROLE to recover the principal

contract RevertingTreasury {
    // No receive() — any ETH push reverts
}
```

The `_collectInterestToTreasury` revert at line 958 propagates through `emergencyWithdrawFromAave` at line 558, and no alternative recovery path exists for `PAUSER_ROLE`. [4](#0-3)

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

**File:** contracts/LRTWithdrawalManager.sol (L945-960)
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
```
