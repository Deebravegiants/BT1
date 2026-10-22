# [M] DEPOSIT_VAULT_ADMIN_ROLE/REDEMPTION_-

## Summary
Severity: Medium
Contest weight: 0.5839
Dataset id: 22800
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The accessibility of DEPOSIT_VAULT_ADMIN_ROLE and REDEMPTION_VAULT_ADMIN_ROLE has larger permission than what the contest readme claims: they can pause the vault and stop users from depositing/redeeming. According to the contest readme: • DEPOSIT_VAULT_ADMIN_ROLE has the role of Handles freeFromMinDeposit, setMinAmountToDeposit, withdrawToken, addPaymentToken, removePaymentToken in DepositVault. • REDEMPTION_VAULT_ADMIN_ROLE has the role of Handles withdrawToken, addPaymentToken, removePaymentToken in RedemptionVault. However, these two roles are also capable of pausing the depositVault/redemptionVault, which is unexpected.
```solidity
modifier onlyPauseAdmin() {
    _onlyRole(pauseAdminRole(), msg.sender);
    _;
}
/**
 * @dev upgradeable pattern contract`s initializer
 * @param _accessControl MidasAccessControl contract address
 */
// solhint-disable-next-line func-name-mixedcase
function __Pausable_init(address _accessControl) internal onlyInitializing {
    __WithMidasAccessControl_init(_accessControl);
}
function pause() external onlyPauseAdmin {
    _pause();
}
function unpause() external onlyPauseAdmin {
    _unpause();
}
```
```solidity
function vaultRole() public view override returns (bytes32) {
    return pauseAdminRole();
}
```
```solidity
function pauseAdminRole() public view override returns (bytes32) {
    return vaultRole();
}
```
```solidity
function vaultRole() public pure override returns (bytes32) {
    return DEPOSIT_VAULT_ADMIN_ROLE;
}
```
```solidity
function vaultRole() public pure override returns (bytes32) {
    return REDEMPTION_VAULT_ADMIN_ROLE;
}
```
The two roles DEPOSIT_VAULT_ADMIN_ROLE/REDEMPTION_VAULT_ADMIN_ROLE have larger permission than they are expected to have.

## Recommendation
Remove the pausability permission for DEPOSIT_VAULT_ADMIN_ROLE and REDEMPTION_VAULT_ADMIN_ROLE.
