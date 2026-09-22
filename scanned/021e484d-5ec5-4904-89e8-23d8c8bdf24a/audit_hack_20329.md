# [C] 5.1.2 ThecastApproval/castDisapprovaldoesn't check ifroleparameter is theapprovalRole

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** LlamaCore.sol#L
**Description:** A policyholder should be able tocasttheir approval for anactionif they have theapprovalRole
defined in the strategy. It should not be possible for otherrolesto cast an action.
The_castApprovalmethod verifies if the policyholder has therolepassed as an argument but doesn't check if it
actually hasapprovalRolewhich is eligible to cast an approval.
This means any role in the llama contract can participate in the approval with completely differentquantities
(weights).
The same problem occurs for thecastDisapprovalfunction as well.
**Recommendation:** The check could be added inside the strategy in thegetApprovalQuantityAtfunction: Rela-
tiveStrategy.sol#L
function getApprovalQuantityAt(address policyholder, uint8 role, uint256 timestamp) external view
,! returns (uint128) {
+ if (role != approvalRole) return 0;
uint128 quantity = policy.getPastQuantity(policyholder, role, timestamp);
return quantity > 0 && forceApprovalRole[role]? type(uint128).max : quantity;
}

If the passedroledoesn't equal theapprovalRolea quantity of zero could be returned.
if (role != approvalRole) return 0;

**Llama:** Fixed in commit 38b5a9.
**Spearbit:** Resolved.
