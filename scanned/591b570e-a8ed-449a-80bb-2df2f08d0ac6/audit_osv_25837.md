# [M] Authenticated SQL Injection in leantime

## Summary
Severity: Medium
Advisory: CVE-2023-45826
Aliases: GHSA-559g-3h98-g3fj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-19
Source: https://osv.dev/vulnerability/CVE-2023-45826
Type: osv

## Details
Leantime is an open source project management system. A 'userId' variable in `app/domain/files/repositories/class.files.php` is not parameterized. An authenticated attacker can send a carefully crafted POST request to `/api/jsonrpc` to exploit an SQL injection vulnerability. Confidentiality is impacted as it allows for dumping information from the database. This issue has been addressed in version 2.4-beta-4. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45826.json
- https://github.com/Leantime/leantime/security/advisories/GHSA-559g-3h98-g3fj
- https://nvd.nist.gov/vuln/detail/CVE-2023-45826
- https://github.com/Leantime/leantime/commit/be75f1e0f311d11c00a0bdc7079a62eef3594bf0
