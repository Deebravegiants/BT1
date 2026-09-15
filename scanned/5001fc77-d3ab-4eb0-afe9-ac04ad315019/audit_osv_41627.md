# [M] CVE-2026-62641

## Summary
Severity: Medium
Advisory: CVE-2026-62641
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-62641
Type: osv

## Details
In Roundcube Webmail before 1.6.17 and 1.7.x before 1.7.2, the TNEF decoder was subject to denial of service via a crafted compressed-RTF size.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.17
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.2
- https://roundcube.net/news/2026/07/05/security-updates-1.6.17-and-1.7.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62641.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-62641
- https://github.com/roundcube/roundcubemail/commit/6d1004fd3764a9606c53130b322c0f295c38be64
- https://github.com/roundcube/roundcubemail/commit/bf253c72d4293c93fda511b8464fe9cb34b522c1
