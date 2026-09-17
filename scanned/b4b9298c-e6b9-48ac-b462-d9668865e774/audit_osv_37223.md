# [M] CVE-2026-29905

## Summary
Severity: Medium
Advisory: CVE-2026-29905
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-29905
Type: osv

## Details
Kirby CMS through 5.1.4 allows an authenticated user with 'Editor' permissions to cause a persistent Denial of Service (DoS) via a malformed image upload. The application fails to properly validate the return value of the PHP getimagesize() function. When the system attempts to process this file for metadata or thumbnail generation, it triggers a fatal TypeError.

## References
- https://drive.google.com/file/d/1MwvvSYIwnC8kOIzjycGMQZw4d2K2ef8h/view?usp=sharing
- https://github.com/getkirby/kirby/releases/tag/5.2.0-rc.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29905.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29905
- https://github.com/Stalin-143/CVE-2026-29905
