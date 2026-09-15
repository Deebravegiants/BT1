# [M] Group-Office Has Authenticated SQL Injection in advancedQueryData.comparator

## Summary
Severity: Medium
Advisory: CVE-2026-27832
Aliases: GHSA-vfgv-8w8v-qpxr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-27832
Type: osv

## Details
Group-Office is an enterprise customer relationship management and groupware tool. Versions prior to 26.0.8, 25.0.87, and 6.8.153 have a SQL Injection (SQLi) vulnerability, exploitable through the `advancedQueryData` parameter (`comparator` field) on an authenticated endpoint. The endpoint `index.php?r=email/template/emailSelection` processes `advancedQueryData` and forwards the SQL comparator without a strict allowlist into SQL condition building. This enables blind boolean-based exfiltration of the `core_auth_password` table. Versions 26.0.8, 25.0.87, and 6.8.153 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27832.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-vfgv-8w8v-qpxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27832
