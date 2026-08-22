# [H] Unauthorized Role Modification Vulnerability in setRole Function

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-28
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/70
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xcac9230f2dc40110a888f845f4e7337b88cbd193f8110efb6f7c010d9e074bd1
**Severity:** high

**Description:**
**Description**:
In the `setRole` function:
```solidity
    /// @param user User that will have specific role (Can be EAO or safe)
    /// @param safeId Safe Id which will have the user permissions on
    function setRole(
```
The `safeId` parameter is intended to specify the safe on which the user will have permissions. However, the current implementation assigns roles to the user without considering the `safeId`. This means roles are assigned to the user generally, not just for that specific `safeId`:
```solidity
        RolesAuthority _authority = RolesAuthority(rolesAuthority);
        _authority.setUserRole(user, uint8(role), enabled);
```
This allows any root to enable or disable any role for any user without restriction, so the root of any organization can enable or disable roles for any user.

**Scenario:**
1. There is an organization called `uniOrg`. This organization assigns user A to role A. A malicious attacker creates an organization called `XOrg` with one safe in his organization. This malicious root can call `setRole` with his `safeId` and user A's address to disable role A for user A or assign any other role to user A.
2. If a user has a `SAFE_LEAD_MODIFY_OWNERS_ONLY` role in an organization and leads safe ID 2, they could create a new organization with another safe wallet and assign `SAFE_LEAD_EXEC_ON_BEHALF_ONLY` to their address.

**Impact:**
- Malicious users can assign any role to any user or assign roles to themselves, allowing them to execute unauthorized transactions.
- Malicious users can revoke roles, causing denial of service (DoS) to other organizations.

**Proof of Concept (PoC):**
Add the following test to `PalmeraRolesTest.t.sol`:
```solidity
function testCan_ROOT_SAFE_SetRole_Issue() public {
        (uint256 rootId, uint256 safeA1Id) =
            palmeraSafeBuilder.setupRootOrgAndOneSafe(orgName, safeA1Name);

        address rootAddr = palmeraModule.getSafeAddress(rootId);
        address userEOALead = address(0x123);
        // Root of the first organization assigns `SAFE_LEAD_MODIFY_OWNERS_ONLY` role to userEOALead.
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/70_
