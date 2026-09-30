# [M] Collateral can still be allocated to PartyA when the system is paused

## Summary
Severity: Medium
Contest weight: 0.6919
Dataset id: 22944
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Collateral can still be allocated to PartyA when the system is paused by exploiting the new internal transfer function.
The allocate and depositAndAllocate functions are guarded by the whenNotAccountingPaused modifier to ensure that collateral can only be allocated when the accounting is not paused.
```solidity
/// @notice Allows Party A to allocate a specified amount of collateral. Allocated amounts are which user can actually trade on.
/// @param amount The precise amount of collateral to be allocated, specified in 18 decimals.
function allocate(uint256 amount) external whenNotAccountingPaused notSuspended(msg.sender) notLiquidatedPartyA(msg.sender) {
    AccountFacetImpl.allocate(amount);
..SNIP..
}

/// @notice Allows Party A to deposit a specified amount of collateral and immediately allocate it.
/// @param amount The precise amount of collateral to be deposited and allocated, specified in collateral decimals.
function depositAndAllocate(uint256 amount) external whenNotAccountingPaused notLiquidatedPartyA(msg.sender) notSuspended(msg.sender) {
    AccountFacetImpl.deposit(msg.sender, amount);
    uint256 amountWith18Decimals = (amount * 1e18) / (10 ** IERC20Metadata(GlobalAppStorage.layout().collateral).decimals());
    AccountFacetImpl.allocate(amountWith18Decimals);
..SNIP..
}
```
However, malicious users can bypass this restriction by exploiting the newly (globalPaused) and accounting pause (accountingPaused) are enabled, malicious users can use the AccountFacet.internalTransfer function, which is not guarded by the whenNotAccountingPaused modifier, to continue allocating collateral to their accounts, effectively bypassing the pause.
```solidity
/// @notice Transfers the sender's deposited balance to the user allocated balance.
/// @dev The sender and the recipient user cannot be partyB.
/// @dev PartyA should not be in the liquidation process.
/// @param user The address of the user to whom the amount will be allocated.
/// @param amount The amount to transfer and allocate in 18 decimals.
function internalTransfer(address user, uint256 amount) external whenNotAccountingPaused whenNotInternalTransferPaused notPartyB userNotPartyB(user) notSuspended(msg.sender) notLiquidatedPartyA(user){
    AccountFacetImpl.internalTransfer(user, amount);
..SNIP..
}
```
When the global pause (globalPaused) and accounting pause (accountingPaused) are enabled, this might indicate that:
1) There is an issue, error, or bug in certain areas (e.g., accounting) of the system. Thus, the funds transfer should be halted to prevent further errors from accumulating and to prevent users from suffering further losses due to this issue
2) There is an ongoing attack in which the attack path involves transferring/allocating funds to an account. Thus, the global pause (globalPaused) and accounting pause (accountingPaused) have been activated to stop the attack. However, it does not work as intended, and the hackers can continue to exploit the system by leveraging the new internal transfer function to workaround the restriction.
In both scenarios, this could lead to a loss of assets.

## Recommendation
```solidity
function internalTransfer(address user, uint256 amount) external whenNotInternalTransferPaused notPartyB userNotPartyB(user) notSuspended(msg.sender) notLiquidatedPartyA(user){
    AccountFacetImpl.internalTransfer(user, amount);
```
