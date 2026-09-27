# [H] ERPNext: Possibility of SQL Injection due to missing validation

## Summary
Severity: High
Advisory: CVE-2026-44446
Aliases: GHSA-6fm9-g88m-hxr7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44446
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.104.3 and 16.14.0, some endpoints were vulnerable to SQL injection through specially crafted requests, which would allow a malicious actor to extract sensitive information. This vulnerability is fixed in 15.104.3 and 16.14.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44446.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-6fm9-g88m-hxr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44446
