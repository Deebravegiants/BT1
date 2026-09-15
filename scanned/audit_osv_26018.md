# [H] CVE-2023-49471

## Summary
Severity: High
Advisory: CVE-2023-49471
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-10
Source: https://osv.dev/vulnerability/CVE-2023-49471
Type: osv

## Details
Blind Server-Side Request Forgery (SSRF) vulnerability in karlomikus Bar Assistant before version 3.2.0 does not validate a parameter before making a request through Image::make(), which could allow authenticated remote attackers to execute arbitrary code.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49471.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49471
- https://github.com/zunak/CVE-2023-49471
