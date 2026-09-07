# [H] `setRole` Function Incorrectly Assigns `_safe.lead` without Validating `enabled` Parameter

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/41
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xbf10b39a27d651c17d6761180193456a8268a6128535dc785370130b083e2c69
**Severity:** high

**Description:**
**Description**:
The `setRole` function assigns the `_safe.lead` attribute to a user if the role is related to safe leadership (`SAFE_LEAD`, `SAFE_LEAD_EXEC_ON_BEHALF_ONLY`, `SAFE_LEAD_MODIFY_OWNERS_ONLY`). However, the function fails to check the `enabled` boolean parameter before updating `_safe.lead`. This can lead to unauthorized access control issues where users might be improperly assigned as safe leads.

**Impact:**
This oversight can result in unauthorized access control, allowing users to be incorrectly recognized as safe leads even if their role was meant to be disabled. This compromises the security and integrity of the system.

**Proof of Concept (PoC):**
Consider the current implementation of the `setRole` function:
```solidity
function setRole(uint256 safeId, address user, uint8 role, bool enabled)
    external
    IsRootSafe(_msgSender())
    requiresAuth
{
    bytes32 org = getOrgBySafe(safeId);
    DataTypes.Safe storage _safe = safes[org][safeId];

    if (
        role == DataTypes.Role.SAFE_LEAD
            || role == DataTypes.Role.SAFE_LEAD_EXEC_ON_BEHALF_ONLY
            || role == DataTypes.Role.SAFE_LEAD_MODIFY_OWNERS_ONLY
    ) {
        // Update safe/org lead
        _safe.lead = user;
    }
}
```
In the above code, `_safe.lead` is assigned to `user` without checking if `enabled` is `true`. This means users could inadvertently be granted lead roles.

**Mitigation:**
1. **Validate the `enabled` Parameter:**
   Ensure the `enabled` parameter is checked before updating `_safe.lead`.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/41_
