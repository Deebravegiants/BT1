# [H] CVE-2024-44313

## Summary
Severity: High
Advisory: CVE-2024-44313
Aliases: GHSA-gg2f-r4jh-vpmh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-03-18
Source: https://osv.dev/vulnerability/CVE-2024-44313
Type: osv

## Details
TastyIgniter 3.7.6 contains an Incorrect Access Control vulnerability in the invoice() function within Orders.php which allows unauthorized users to access and generate invoices due to missing permission checks.

## References
- https://github.com/tastyigniter/TastyIgniter/blob/3.x/app/admin/controllers/Orders.php
- https://medium.com/@cnetsec/cve-2024-44313-incorrect-access-control-in-tastyigniter-3-7-6-01a73c548b74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44313.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44313
