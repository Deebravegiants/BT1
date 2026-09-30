# [M] Admin will not be able to only

## Summary
Severity: Medium
Contest weight: 0.5630
Dataset id: 2586
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The modifier LVDepositNotPaused in Vault::depositLv() checks states[id].vault.config.isWithdrawalPaused instead of states[id].vault.config.isDepositPaused, which means deposits will only be paused if withdrawals are paused, DoSing withdrawals. In ModuleState:109, it checks states[id].vault.config.isWithdrawalPaused when it should check states[id].vault.config.isDepositPaused. Internal pre-conditions 1. Admin pauses deposits. External pre-conditions None. Attack Path 1. Admin sets deposits paused, but deposits are not actually paused due to the incorrect modifier. 2. Admin either leaves deposits unpaused or pauses both deposits and withdrawals, DoSing withdrawals. Admin is not able to pause deposits alone which would lead to loss of funds as this is an emergency mechanism. If the admin wants to pause deposits, withdrawals would also have to be paused, DoSing withdrawals.

## Proof of Concept
ModuleState::LVDepositNotPaused() is incorrect:
```solidity
modifier LVDepositNotPaused(Id id) {
    revert LVDepositPaused();
    _;
}
```

## Recommendation
ModuleState::LVDepositNotPaused() should be:
```solidity
modifier LVDepositNotPaused(Id id) {
    if (states[id].vault.config.isDepositPaused) {
        revert LVDepositPaused();
    }
    _;
}
```
