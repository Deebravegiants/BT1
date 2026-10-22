# [M] 6.2 Inconsistent Access Control

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

The setup of roles for the contract CoreBorrow is implemented in the function initialize. The admin
of the GUARDIAN_ROLE is set to GUARDIAN_ROLE, which may lead to an exploit as a malicious guardian
can remove all governors from the GUARDIAN_ROLE. In such scenario, the functions addGovernor,
isGovernorOrGuardian, and all the functions in other contracts that call isGovernorOrGuardian
with a governor address would revert, as they no longer have the GUARDIAN_ROLE, and thus are no
longer the admin of the GUARDIAN_ROLE.

```
function initialize(address governor, address guardian) public initializer {
require(governor != address(0) && guardian != address(0), "O");
require(governor != guardian, "12");
_setupRole(GOVERNOR_ROLE, governor);
_setupRole(GUARDIAN_ROLE, guardian);
_setupRole(GUARDIAN_ROLE, governor);
_setRoleAdmin(GUARDIAN_ROLE, GUARDIAN_ROLE);
_setRoleAdmin(FLASHLOANER_TREASURY_ROLE, GOVERNOR_ROLE);
}
```
```
function addGovernor(address governor) external {
grantRole(GOVERNOR_ROLE, governor);
grantRole(GUARDIAN_ROLE, governor);
}
```
```
function isGovernorOrGuardian(address admin) external view returns (bool) {
return hasRole(GUARDIAN_ROLE, admin);
}
```
Code corrected:

The issue has been addressed in code Version 2, the governor is set as the admin of the
GUARDIAN_ROLE, hence a guardian cannot change anymore the roles of a governor address.


Furthermore, the function removeGovernor has been updated to allow a governor address to remove
its roles, i.e., revoke its roles as guardian and then as governor.
