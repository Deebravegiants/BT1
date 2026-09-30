# [M] CVE-2026-39229

## Summary
Severity: Medium
Advisory: CVE-2026-39229
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-39229
Type: osv

## Details
Bolt CMS through 3.7.0 allows SQL Injection in the 'order' parameter of the content listing pages. An authenticated attacker with low-level privileges can exploit this through the OrderDirective component. This allows for the extraction of sensitive information

## References
- https://boltcms.io/
- https://github.com/Tonoss-412/My-CVE/blob/main/CVE-2026-39229.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39229.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39229
- https://github.com/bolt/bolt
