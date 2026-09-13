# [H] CVE-2026-48844

## Summary
Severity: High
Advisory: CVE-2026-48844
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/CVE-2026-48844
Type: osv

## Details
Roundcube Webmail 1.6.x before 1.6.16 and 1.7.x before 1.7.1 has insecure code evaluation logic in LDAP the autovalues option that could lead to code injection. (Support for code evaluation has been removed in 1.6.16 and 1.7.1.)

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.16
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.1
- https://roundcube.net/news/2026/05/24/security-updates-1.6.16-and-1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48844.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48844
- https://github.com/roundcube/roundcubemail/commit/6a777d7394b763ce9acfce86c1a521e14a02d862
- https://github.com/roundcube/roundcubemail/commit/ea1798a6fbf060abcc0ba73b2435036bf8016a5a
