# [M] CVE-2026-75010

## Summary
Severity: Medium
Advisory: CVE-2026-75010
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75010
Type: osv

## Details
In Roundcube Webmail before 1.6.18 and 1.7.x before 1.7.3, the modoboa driver of the password plugin could leak a Modoboa API authentication token to a user-controlled host via crafted session data. This issue only affects Roundcube instances using the password plugin with its modoboa driver.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.18
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.3
- https://roundcube.net/news/2026/08/09/security-updates-1.6.18-and-1.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75010.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75010
- https://github.com/roundcube/roundcubemail/commit/65b8ea9d8304b10f1d3bda5bcc82f9c682cf804c
- https://github.com/roundcube/roundcubemail/commit/b0e26d617e7bbe3051135285993bc55f718fea2f
