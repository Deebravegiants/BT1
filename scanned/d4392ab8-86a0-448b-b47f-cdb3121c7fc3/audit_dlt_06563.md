# [H] `isSafeLead` Function Lacks Role Authorization Check, Leading to Unauthorized Access

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/38
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x01ce89127e51d210fc9c3358de869c569bc2ba304b9ab3acd986826a210e07b9
**Severity:** high

**Description:**
**Description**:
The `isSafeLead` function determines if a user is a lead for a given safe by checking the `_safe.lead` attribute. However, this approach does not account for scenarios where the user's Safe Lead roles have been revoked through the `disableSafeLeadRoles` function. This can result in unauthorized access because the function does not verify the user's current roles in the `RolesAuthority` contract.

**Impact:**
This oversight allows users whose roles have been revoked to still be recognized as safe leads, potentially leading to unauthorized actions and compromising the access control mechanism.

**Proof of Concept (PoC):**
1. Assume a user `X` is initially assigned as a lead for `safe B`.
2. The `disableSafeLeadRoles` function is called on user `X`, revoking all their Safe Lead roles.
3. Despite the revocation, the `isSafeLead` function continues to identify `X` as a lead for `safe B` because it only checks the `_safe.lead` attribute and not the user's current roles.

Current `isSafeLead` implementation:
```solidity
function isSafeLead(uint256 safeId, address user)
    public
    view
    returns (bool)
{
    bytes32 org = getOrgBySafe(safeId);
    DataTypes.Safe memory _safe = safes[org][safeId];
    if (_safe.safe == address(0)) return false;
    if (_safe.lead == user) {
        return true;
    }
    return false;
}
```

**Mitigation:**
Update the `isSafeLead` function to include a check against the `RolesAuthority` to confirm the user still holds the relevant Safe Lead roles.
