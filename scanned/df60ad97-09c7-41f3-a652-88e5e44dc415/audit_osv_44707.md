# [C] snipe-it before 8.6.3 Authorization Bypass via Bulk Delete

## Summary
Severity: Critical
Advisory: CVE-2026-85617
Aliases: GHSA-mx3g-8v84-j6gg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85617
Type: osv

## Details
snipe-it versions before 8.6.3 contain an authorization bypass vulnerability in the bulk delete functionality that allows restricted users to soft-delete users outside their authorized scope. Attackers can include unauthorized user IDs in bulk delete requests to bypass instance-level restrictions and modify or disable accounts they should not access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85617.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-mx3g-8v84-j6gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-85617
- https://www.vulncheck.com/advisories/snipe-it-before-8.6.3-authorization-bypass-via-bulk-delete
