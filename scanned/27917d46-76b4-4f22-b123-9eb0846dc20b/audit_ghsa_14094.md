# [M] Pimcore vulnerable to Business Logic Errors via Customer automation rules

## Summary
Severity: Medium
Advisory: GHSA-x99j-r8vv-gwwj
CVE: CVE-2023-32075
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-x99j-r8vv-gwwj
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <3.3.9

## Details
### Impact
Business Logic Errors in the Conditions tab since the counter can be a negative number.

This vulnerability is capable of the unlogic in the counter value in the Conditions tab.

### Patches
Update to version 3.3.9 or apply this patch manually https://github.com/pimcore/customer-data-framework/commit/e3f333391582d9309115e6b94e875367d0ea7163.patch

### Workarounds
Apply https://github.com/pimcore/customer-data-framework/commit/e3f333391582d9309115e6b94e875367d0ea7163.patch manually.

### References
https://huntr.dev/bounties/cecd7800-a996-4f3a-8689-e1c2a1e0248a/

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-x99j-r8vv-gwwj
- https://nvd.nist.gov/vuln/detail/CVE-2023-32075
- https://github.com/pimcore/customer-data-framework/commit/e3f333391582d9309115e6b94e875367d0ea7163.patch
- https://github.com/pimcore/customer-data-framework
- https://github.com/pimcore/customer-data-framework/releases/tag/v3.3.9
- https://huntr.dev/bounties/cecd7800-a996-4f3a-8689-e1c2a1e0248a
