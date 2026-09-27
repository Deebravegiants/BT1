# [M] Rallly Information Disclosure Vulnerability in Participant API Leaks Names and Emails Despite Pro Privacy Settings

## Summary
Severity: Medium
Advisory: CVE-2025-66027
Aliases: GHSA-65wg-8xgw-f3fg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66027
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.6, an information disclosure vulnerability exposes participant details, including names and email addresses through the /api/trpc/polls.get,polls.participants.list endpoint, even when Pro privacy features are enabled. This bypasses intended privacy controls that should prevent participants from viewing other users’ personal information. This issue has been patched in version 4.5.6.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66027.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-65wg-8xgw-f3fg
- https://nvd.nist.gov/vuln/detail/CVE-2025-66027
- https://github.com/lukevella/rallly/commit/59738c04f9a8ec25f0af5ce20ad0eab6cf134963
