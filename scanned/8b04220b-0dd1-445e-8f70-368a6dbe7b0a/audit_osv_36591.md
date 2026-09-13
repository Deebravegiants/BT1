# [M] Open eClass is Vulnerable to Username Enumeration via Login Response Discrepancies

## Summary
Severity: Medium
Advisory: CVE-2026-24664
Aliases: GHSA-c3wq-m629-5h2j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-24664
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, a username enumeration vulnerability allows unauthenticated attackers to identify valid user accounts by analyzing differences in the login response behavior. This issue has been patched in version 4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24664.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-c3wq-m629-5h2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-24664
