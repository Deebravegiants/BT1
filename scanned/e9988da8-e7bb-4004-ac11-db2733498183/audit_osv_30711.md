# [H] Data leak through CORS misconfiguration in stitionai/devika

## Summary
Severity: High
Advisory: CVE-2024-5549
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-5549
Type: osv

## Details
A CORS misconfiguration in the stitionai/devika repository allows attackers to steal sensitive information such as logs, browser sessions, and settings containing private API keys from other services. This vulnerability also enables attackers to perform actions on behalf of the user, such as deleting projects or sending messages. The issue arises from the lack of proper origin validation, allowing unauthorized cross-origin requests to be executed. The vulnerability is present in all versions of the repository, as no fixed version has been specified.

## References
- https://huntr.com/bounties/7ffeb896-27c8-429d-b241-4f7d6dda0afd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5549.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5549
- https://github.com/stitionai/devika/commit/6acce21fb08c3d1123ef05df6a33912bf0ee77c2
