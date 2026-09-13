# [M] Snipe-IT before 8.7.0 Missing Authorization via asset-history CSV importer

## Summary
Severity: Medium
Advisory: CVE-2026-86759
Aliases: GHSA-2232-926w-qvr9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86759
Type: osv

## Details
Snipe-IT versions before 8.7.0 fail to authorize the POST /hardware/history endpoint, allowing any authenticated user to reassign arbitrary assets and modify audit logs. Attackers can submit a CSV file to reassign assets across companies and inject fraudulent audit trail entries, compromising inventory integrity and accountability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86759.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-2232-926w-qvr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-86759
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-missing-authorization-via-asset-history-csv-importer
