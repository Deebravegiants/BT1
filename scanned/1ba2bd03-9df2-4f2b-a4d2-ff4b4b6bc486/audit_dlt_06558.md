# [M] `addSafe` Function Lacks Validation for `superSafeId` State

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-25
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/52
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x93fccb92b363ffdf511e64f3b1acb16fa808c07792bc8eac27a02d51ceb892a0
**Severity:** medium

**Description:**
**Description**:
The `addSafe` function does not check if the provided `superSafeId` is in a removed state. This oversight can lead to a scenario where a removed safe ID is incorrectly set as a `superSafeId`, potentially causing logical inconsistencies and security issues.

**Impact:**
Allowing a removed safe ID to become a `superSafeId` can compromise the integrity of the hierarchical structure of safes. safes, that are removed, but not disconnected shouldn't become super safe again.



**Mitigation:**
Add a check to ensure that the `superSafeId` is not in a removed state before proceeding with the addition of the new safe.
