# [H] CVE-2024-56073

## Summary
Severity: High
Advisory: CVE-2024-56073
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-15
Source: https://osv.dev/vulnerability/CVE-2024-56073
Type: osv

## Details
An issue was discovered in FastNetMon Community Edition through 1.2.7. Zero-length templates for Netflow v9 allow remote attackers to cause a denial of service (divide-by-zero error and application crash).

## References
- https://cwe.mitre.org/data/definitions/369.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56073.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56073
- https://github.com/pavel-odintsov/fastnetmon/commit/a36718525e08ad0f2a809363001bf105efc5fe1c
