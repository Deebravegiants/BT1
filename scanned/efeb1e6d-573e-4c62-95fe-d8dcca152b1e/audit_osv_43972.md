# [M] CVE-2026-76956

## Summary
Severity: Medium
Advisory: CVE-2026-76956
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-76956
Type: osv

## Details
In libexpat 2.8.2 and 2.8.3 before 2.8.4, misinterpretation of getentropy's return code leads to insufficient entropy, which results in being vulnerable to hash flooding attacks, causing a denial of service via crafted XML content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76956.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76956
- https://github.com/libexpat/libexpat/pull/1326
- https://github.com/libexpat/libexpat/pull/1329
