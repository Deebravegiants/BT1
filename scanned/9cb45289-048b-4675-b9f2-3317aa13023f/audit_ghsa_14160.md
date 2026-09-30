# [H] Embedding untrusted input inside CSV files leads to Formula Injection/CSV Injection

## Summary
Severity: High
Advisory: GHSA-mq3x-qgwx-3rfw
CVE: CVE-2023-2629
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-mq3x-qgwx-3rfw
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <3.3.9

## Details
### Impact
The pimcore application is vulnerable to Formula Injection/CSV Injection via the Firstname, Lastname, Street, Zip & City input fields. These vulnerabilities allow unauthenticated attackers to execute arbitrary code via a crafted excel file.

Successful exploitation can lead to impacts such as client-sided command injection, code execution, or remote ex-filtration of contained confidential data.

### Patches
Update to version 3.3.9 or apply this patch manually https://github.com/pimcore/customer-data-framework/commit/4e0105c3a78d20686a0c010faef27d2297b98803.patch

### Workarounds
Apply patch https://github.com/pimcore/customer-data-framework/commit/4e0105c3a78d20686a0c010faef27d2297b98803.patch manually.

### References
https://huntr.dev/bounties/821ff465-4754-42d1-9376-813c17f16a01/

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-mq3x-qgwx-3rfw
- https://nvd.nist.gov/vuln/detail/CVE-2023-2629
- https://github.com/pimcore/customer-data-framework/commit/4e0105c3a78d20686a0c010faef27d2297b98803
- https://github.com/pimcore/customer-data-framework
- https://huntr.dev/bounties/821ff465-4754-42d1-9376-813c17f16a01
