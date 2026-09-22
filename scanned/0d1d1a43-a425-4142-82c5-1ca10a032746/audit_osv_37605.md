# [M] OpenEMR: Missing Authorization on Claim File Tracker UI and AJAX Endpoint (V2)

## Summary
Severity: Medium
Advisory: CVE-2026-32122
Aliases: GHSA-rwf9-px3c-3prw
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32122
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.1, the Claim File Tracker feature exposes an AJAX endpoint that returns billing claim metadata (claim IDs, payer info, transmission logs). The endpoint does not enforce the same ACL as the main billing/claims workflow, so authenticated users without appropriate billing permissions can access this data. This vulnerability is fixed in 8.0.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32122.json
- https://github.com/openemr/openemr/security/advisories/GHSA-rwf9-px3c-3prw
- https://nvd.nist.gov/vuln/detail/CVE-2026-32122
