# [H] Data Space Portal: Incorrect Authorization and Client-Side Enforcement of Server-Side Security in ghcr.io/sovity/ds-portal-ce-backend

## Summary
Severity: High
Advisory: CVE-2026-42160
Aliases: GHSA-989g-wpfv-6vxx
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:H/SI:H/SA:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42160
Type: osv

## Details
Data Space Portal is an open-source Software as a Service (SaaS) solution designed to streamline Dataspace management. From version 2.1.1 to before version 7.3.2, there is insufficient authorization in the dataspace-portal backend regarding self-registered "PENDING" organization / user accounts. This issue has been patched in version 7.3.2.

## References
- https://github.com/sovity/dataspace-portal/releases/tag/v7.3.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42160.json
- https://github.com/sovity/dataspace-portal/security/advisories/GHSA-989g-wpfv-6vxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-42160
