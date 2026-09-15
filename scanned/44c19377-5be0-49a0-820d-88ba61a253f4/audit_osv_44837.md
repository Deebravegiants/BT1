# [M] Snipe-IT before 8.7.0 License Key Exposure via CSV Export

## Summary
Severity: Medium
Advisory: CVE-2026-86758
Aliases: GHSA-5jcj-c9p3-82q7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86758
Type: osv

## Details
Snipe-IT before 8.7.0 fails to properly enforce the viewKeys authorization gate in CSV export and API index endpoints, allowing authenticated users with only licenses.view permission to access product keys. Attackers can download all license keys in bulk via CSV export or validate candidate keys through API response discrepancies without needing the viewKeys permission.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86758.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-5jcj-c9p3-82q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-86758
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-license-key-exposure-via-csv-export
