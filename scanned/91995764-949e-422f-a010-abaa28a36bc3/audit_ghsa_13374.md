# [M] Pimcore Customer Management Framework vulnerable to Improper Authorization in Rules Controller

## Summary
Severity: Medium
Advisory: GHSA-vx35-f379-4q49
CVE: CVE-2023-3574
CWE: CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-10
Source: https://github.com/advisories/GHSA-vx35-f379-4q49
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <3.4.1

## Details
### Impact
The product performs authorization checks incorrectly when an unauthorized actor tries to access a resource or perform an actions.

The attacker can view and freely perform actions to add, modify, or delete rules.

### Patches
Update to version 3.4.1 or apply this patch manually https://github.com/pimcore/customer-data-framework/commit/f15668c86db254e86ba7ac895bc3cdd1a2a3cc45.patch

### Workarounds
Apply https://github.com/pimcore/customer-data-framework/commit/f15668c86db254e86ba7ac895bc3cdd1a2a3cc45.patch manually.

### References
https://huntr.dev/bounties/1dcb4f01-e668-4aa3-a6a3-838532e500c6/

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-vx35-f379-4q49
- https://nvd.nist.gov/vuln/detail/CVE-2023-3574
- https://github.com/pimcore/customer-data-framework/commit/f15668c86db254e86ba7ac895bc3cdd1a2a3cc45
- https://github.com/pimcore/customer-data-framework/commit/f15668c86db254e86ba7ac895bc3cdd1a2a3cc45.patch
- https://github.com/pimcore/customer-data-framework
- https://huntr.dev/bounties/1dcb4f01-e668-4aa3-a6a3-838532e500c6
