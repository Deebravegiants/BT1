# [M] Freezing roles in GranularRoles does not prevent ADMIN_ROLE from modifying roles

## Summary
Severity: Medium
Contest weight: 0.2006
Dataset id: 17750
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In ERC721NFTProduct and ERC1155NFTProduct roles can be frozen which is supposed to lock role to current addresses and not allow any changes. The problem is that admin can still use AccessControlUpgradable#grantRole and revokeRole to grant and remove roles to addresses because hasRole allows "ADMIN_ROLE" to bypass all role restrictions even "DEFAULT_ADMIN_ROLE". function hasRole(bytes32 role, address account) public view virtual override returns (bool) { return super.hasRole(ADMIN_ROLE, account) || super.hasRole(role, account); } In GranularRoles.sol and AccessControlUpgradable.sol, developers are careful to never grant the "DEFAULT_ADMIN_ROLE" to any user. Additionally they never set the admin role of any role so that it's admin will remain "DEFAULT_ADMIN_ROLE". In theory this should make so that there is no way to grant or revoke roles outside of GranularRoles#_initRoles and updateRoles. The issue is that the override by GranularRoles#hasRole allows "ADMIN_ROLE" to bypass any role restriction including "DEFAULT_ADMIN_ROLE". This allows "ADMIN_ROLE" to directly call AccessControlUpgradable#grantRole and revokeRole, which makes the entire freezing system useless as it doesn't actually stop any role modification. Freezing roles doesn't actually prevent "ADMIN_ROLE" from modifying roles as intended. Submitting as high due to gross over-extension of admin authority clearly violating intended guardrails.

## Recommendation
Override AccessControlUpgradable#grantRole and revokeRole in GranularRoles.sol to revert when called: GranularRoles.sol + function grantRole(bytes32 role, address account) public virtual override { + revert(); + } + function revokeRole(bytes32 role, address account) public virtual override { + revert(); + }
