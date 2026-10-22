# [M] `setPendingRedemptionBalance`

## Summary
Severity: Medium
Contest weight: 0.6026
Dataset id: 18009
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue is a race‑condition style overwrite in the function that updates a user’s pending redemption balance for a given epoch. The function accepts a user address, an epoch identifier and a new balance value, but it does not verify that the stored balance has not been changed since the caller last read it. Because the contract only checks that the epoch is not in the future, a manager with the MANAGER_ADMIN role can call setPendingRedemptionBalance and write any value, even if the user has already increased the pending amount by calling requestRedemption in the same epoch. If the user’s request is mined after the admin’s transaction (for example by using a higher gas price), the user’s increase is applied first and then the admin’s call overwrites the stored amount with the older value supplied to the admin function. The result is that the user’s pending redemption balance is reduced, effectively causing a loss of the amount that was added by the user. From a user’s perspective the UI may show a lower pending redemption amount than expected, or even zero, despite having submitted a redemption request. The protocol’s accounting assumptions – that the sum of pending redemptions equals the total amount users intend to burn – are violated, leading to missing funds and potential disputes. The flaw was discovered during a manual audit that examined the state‑update logic and identified the missing old‑balance check. It is hard to notice because the contract does not emit an explicit error when the overwrite occurs; the balance simply appears to be set to the admin‑provided value, and no revert is triggered. The recommended mitigation is to require the caller to provide the current stored balance (oldBalance) and to revert if the supplied oldBalance does not match the on‑chain value, thereby enforcing an optimistic‑concurrency guard. Alternative fixes include restricting the admin function to only increase balances, using atomic update patterns, or eliminating the admin‑only balance override altogether. Implementing such a check restores the invariant that a user’s pending redemption amount cannot be unintentionally reduced by concurrent transactions, preserving both user expectations and protocol accounting integrity.

## Proof of Concept
In `setPendingRedemptionBalance()`, `MANAGER_ADMIN` can adjust the amount of the cash token of user to be burned in some cases: addressToBurnAmt[user] Three main parameters are passed in.
    
```solidity
    address user,
    uint256 epoch,
    uint256 balance
```

Before modification will check epoch can not be greater than the currentEpoch, is can modify the currentEpoch user balance.

This has a problem:  
The user is able to increase the addressToBurnAmt[user] of currentEpoch by `requestRedemption()`  
This leaves open the possibility that the user may have unknowingly executed requestRedemption() before settingPendingRedemptionBalance(), causing the increased balance to be overwritten  

For example:  
currentEpoch = 1  
Balance of alice: addressToBurnAmt[alice] = 50

  1. The administrator finds something wrong, there is 10 less, so he wants to increase it by 10, so he calls setPendingRedemptionBalance (balance=60)
  2. Alice does not know the above operation and wants to increase the redemption by 100, so it executes requestRedemption(100), which is executed earlier than setPendingRedemptionBalance() because the gas price is set higher
  3. The result is that the final balance of alice becomes only 60. change process: `50 => 150 => 60`

The result is missing 100.

Suggest adding oldBalance, not equal will revert.

## Recommendation
Adding oldBalance, not equal will revert.
    
```solidity
function setPendingRedemptionBalance(
    address user,
    uint256 epoch,
    uint256 oldBalance    
    uint256 balance
) external updateEpoch onlyRole(MANAGER_ADMIN) {
    if (epoch > currentEpoch) {
      revert CannotServiceFutureEpoch();
    }
    require(oldBalance == redemptionInfoPerEpoch[epoch].addressToBurnAmt[user],"bad old balance");
```
