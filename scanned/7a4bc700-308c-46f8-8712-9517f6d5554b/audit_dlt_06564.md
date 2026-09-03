# [H] Ineffective Revocation of Multiple Roles in `disableSafeLeadRoles` Function

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/37
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x8d23215454d9871dc9515a5530a4c67ebeaa618b59f9802de061fca466b5ca9c
**Severity:** high

**Description:**
**Description**:
The `disableSafeLeadRoles` function is designed to revoke specific Safe Lead roles from a user. However, the current implementation only revokes the first role it encounters and skips the rest. This means if a user has multiple roles, only the first role in the conditional checks is revoked, leaving the other roles intact.

**Impact:**
If a user has more than one Safe Lead role, such as `SAFE_LEAD_EXEC_ON_BEHALF_ONLY` and `SAFE_LEAD_MODIFY_OWNERS_ONLY`, the function will only revoke the `SAFE_LEAD_EXEC_ON_BEHALF_ONLY` role and will not revoke the `SAFE_LEAD_MODIFY_OWNERS_ONLY` role, leading to insufficient role revocation.

**Proof of Concept (PoC)**:
1. Assume a user has the following roles:
   - `SAFE_LEAD_EXEC_ON_BEHALF_ONLY`
   - `SAFE_LEAD_MODIFY_OWNERS_ONLY`
2. The `disableSafeLeadRoles` function is called for this user:
   ```solidity
   function disableSafeLeadRoles(address user) private {
       RolesAuthority _authority = RolesAuthority(rolesAuthority);
       if (_authority.doesUserHaveRole(user, uint8(DataTypes.Role.SAFE_LEAD)))
       {
           _authority.setUserRole(user, uint8(DataTypes.Role.SAFE_LEAD), false);
       } else if (
           _authority.doesUserHaveRole(
               user, uint8(DataTypes.Role.SAFE_LEAD_EXEC_ON_BEHALF_ONLY)
           )
       ) {
           _authority.setUserRole(
               user, uint8(DataTypes.Role.SAFE_LEAD_EXEC_ON_BEHALF_ONLY), false
           );
       } else if (
           _authority.doesUserHaveRole(
               user, uint8(DataTypes.Role.SAFE_LEAD_MODIFY_OWNERS_ONLY)
           )
       ) {
           _authority.setUserRole(
               user, uint8(DataTypes.Role.SAFE_LEAD_MODIFY_OWNERS_ONLY), false
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/37_
