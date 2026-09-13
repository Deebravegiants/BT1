# [M] Open eClass Has Broken Access Control in Course Units Module Allows Students to Create Units

## Summary
Severity: Medium
Advisory: CVE-2026-24670
Aliases: GHSA-4jf5-636r-hv9v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-24670
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, a broken access control vulnerability allows authenticated students to create new course units, an action normally restricted to higher-privileged roles. This issue has been patched in version 4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24670.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-4jf5-636r-hv9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-24670
