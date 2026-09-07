# [H] Incomplete Deletion of Organization State Leads to Residual Effects on New Users

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/27
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x78d66b6486d668178f5595fab64e6f76fb0ff5c60b75adaeaaebed8ed401deb8
**Severity:** high

**Description:**
**Description**:
When organizations are deleted, not all state information about them is completely removed. This can affect new users who register organizations with the same name. Some of these residual states include `allowFeature`, `listed[org]`, and `listCount`.

**Impact**:
New users registering organizations with the same name as previously deleted organizations can inherit unwanted residual states, potentially causing functional and security issues.

**Scenario**:
1. User A registers an organization with the name "xyz".
2. User A calls `addToList` and enables the denylist with `enableDenylist`.
3. After some time, User A's organization "xyz" is deleted but not all related state variables are cleared.
4. A new user registers a new organization with the same name "xyz".
5. The new organization inherits the residual state from the old "xyz" organization.


**Mitigation**
clear all storage varibale related to org in `removeOrg`
