# [H] Unauthorized Access Control Due to Retained Root Role When Root Safe Exits and Joins New Org

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-30
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/76
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x4fa5f750c55d8c00ed572d0c417eb015d71cfca301caef739cb0d4beed582de9
**Severity:** high

**Description:**
**Description:**

When a root safe exits an organization and becomes a member of a new organization, it retains the root role. This leads to unauthorized access as the contract assumes this safe is the root of the new organization. The relevant code snippet from `_createOrgOrRoot` assigns the `ROOT_SAFE` role to the root safe:

```solidity
        /// Assign SUPER_SAFE Role + SAFE_ROOT Role
        RolesAuthority _authority = RolesAuthority(rolesAuthority);
        _authority.setUserRole(
            newRootSafe, uint8(DataTypes.Role.ROOT_SAFE), true
        );
```

**Scenario:**
1. Safe A creates a new organization and becomes the root.
2. Safe A exits this organization.
3. Safe A is added as a member to a new organization.
4. The contract incorrectly assumes Safe A is the root of the new organization due to the retained `ROOT_SAFE` role.

**Impact:**
- Unauthorized access control as the safe retains root privileges in the new organization.

**Mitigation:**

In the `addSafe` function, ensure that any existing `ROOT_SAFE` role is revoked before adding the safe to a new organization. The modified code should look like this:

```diff
@@ -379,6 +379,14 @@ contract PalmeraModule is Auth, Helpers {
         indexSafe[org].push(safeId);
         /// Give Role SuperSafe
         RolesAuthority _authority = RolesAuthority(rolesAuthority);
+        if (_authority.doesUserHaveRole(
+                    newSafe.safe, uint8(DataTypes.Role.ROOT_SAFE))
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/76_
