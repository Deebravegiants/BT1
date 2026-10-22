# [M] Role, permission, strategy, and guard management or config errors

## Summary
Severity: Medium
Contest weight: 0.4825
Dataset id: 9962
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LlamaCore deployment from the factory will only succeed if one of the roles is the BOOTSTRAP_ROLE. As the comments note:
```solidity
// There must be at least one role holder with role ID of 1, since that role ID is initially
// given permission to call `setRolePermission`. This is required to reduce the chance that an
// instance is deployed with an invalid configuration that results in the instance being unusable.
// Role ID 1 is referred to as the bootstrap role.
```
There are still several ways a user can misstep and lose access to LlamaCore.
• Bootstrap Role Scenarios While the bootstrap role is still needed:
1. Setting an expiry on the bootstrap role's policyholder RoleHolderData and allowing the timestamp to pass. Once passed any caller may remove the BOOTSTRAP_ROLE from expired policyholders.
2. Removing the BOOTSTRAP_ROLE from all policyholders.
3. Revoking the role's permission with setRolePermission(BOOTSTRAP_ROLE, bootstrapPermissionId, false).
• General Roles and Permissions Similarly, users may allow other permissions to expire, or remove/revoke them, which can leave the contract in a state where no permissions exist to interact with it. The BOOTSTRAP_ROLE would need to be revoked or otherwise out of use for this to be a problem.
• Misconfigured Strategies A misconfigured strategy may also result in the inability to process new actions. For example:
1. Setting minApprovals too high.
2. Setting queuingPeriod unreasonably high
3. Calling revokePolicy when doing so would make policy.getRoleSupplyAsQuantitySum(approvalRole) fall below minApprovals (or fall below minApprovals - actionCreatorApprovalRoleQty). 1 & 2 but applied to disapprovals. And more, depending on the strategy (e.g. if a strategy always responded true to isActive).
• Removal of Strategies It should not be possible to remove the last strategy of a Llama instance It is possible to remove all strategies from an Ilama instance. It would not be possible to create a new action afterward. An action is required to add other strategies back. As a result, the instance would become unusable, and access to funds locked in the Accounts would be lost.
• Misconfigured Guards An accidentally overly aggressive guard could block all transactions. There is a built-in protection to prevent guards from getting in the way of basic management if (target == address(this) || target == address(policy)) revert CannotUseCoreOrPolicy();. Again, the BOOTSTRAP_ROLE would need to be revoked or otherwise out of use for this to be a problem.

## Recommendation
• Bootstrap Role Given the importance of the bootstrap role, and the factory-level enforcement of its existence, preventing it from expiring would prevent accidental loss of the role. In general, exercise extreme caution when removing or disabling this role.
• General Roles and Permissions In addition to any potential code changes, documentation and UI should highlight the foot guns present when removing role permissions and roles from policyholders (i.e. care must be taken to ensure the remaining permissions/roles support the ongoing operation of LlamaCore).
• Misconfigured Strategies Again, document and surface risks in UI at a minimum. Consider adding on-chain checks if ever possible to prevent strategies that are unable to create/approve/execute actions.
• Removal of Strategies It should not be possible to remove the last strategy of a Llama instance Risk of removing strategies should be documented and surfaced in the UI, as even if one strategy remains, it may not be the strategy needed to support the remaining permissions.
• Misconfigured Guards Similar to strategies, document and surface risks in UI at minimum. Consider adding on-chain checks if ever possible to prevent guards that are unable to create/approve/execute actions.
