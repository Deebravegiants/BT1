# [H] Insufficient Access Control in execTransactionOnBehalf Due to Broad Lead Role Check

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/31
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x7d4876c32195c1fd708d9f45457a3dc78a642b77579a1b97e9ee8c71a7044077
**Severity:** high

**Description:**
# Title
Insufficient Access Control in `execTransactionOnBehalf` Due to Broad Lead Role Check

**Description**:
In the `execTransactionOnBehalf` function, there is a check to bypass the signature verification if the caller is a Safe Lead. However, this check does not distinguish between the different Safe Lead roles (`SAFE_LEAD`, `SAFE_LEAD_EXEC_ON_BEHALF_ONLY`, and `SAFE_LEAD_MODIFY_OWNERS_ONLY`). The current implementation allows any lead role to bypass the signature check, which leads to insufficient access control.

**Impact**:
Insufficient access control, allowing users with any lead role to bypass signature verification and execute transactions on behalf of the safe.

**Proof of Concept (PoC)**:
1. Consider the `execTransactionOnBehalf` function:
   ```solidity
    if (!isSafeLead(getSafeIdBySafe(org, targetSafe), caller)) {
   ```
2. The `isSafeLead` function only checks for the general `_safe.lead`:
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

3. The `setRole` function updates `_safe.lead` for all three lead roles:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/31_
