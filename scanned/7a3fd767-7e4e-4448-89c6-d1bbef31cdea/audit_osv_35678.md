# [C] CVE-2026-12605

## Summary
Severity: Critical
Advisory: CVE-2026-12605
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-12605
Type: osv

## Details
In Eclipse GlassFish versions 8.0.x before 8.0.4, CSRF + SSRF in DownloadServlet ContentSources leaks the admin `gfresttoken` to attacker-controlled host if the victim is authenticated into the Admin Console -\> full unauthenticated takeover of Eclipse GlassFish domain until the token expires.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/127
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/445
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12605.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12605
