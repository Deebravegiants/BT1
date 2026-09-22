# [H] CVE-2022-34127

## Summary
Severity: High
Advisory: CVE-2022-34127
Aliases: GHSA-4hpg-m8fv-xv3h
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2022-34127
Type: osv

## Details
The Managentities plugin before 4.0.2 for GLPI allows reading local files via directory traversal in the inc/cri.class.php file parameter.

## References
- https://github.com/InfotelGLPI/manageentities/releases/tag/4.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/34xxx/CVE-2022-34127.json
- https://github.com/InfotelGLPI/manageentities/security/advisories/GHSA-4hpg-m8fv-xv3h
- https://nvd.nist.gov/vuln/detail/CVE-2022-34127
- https://pentest.blog/advisory-glpi-service-management-software-sql-injection-remote-code-execution-and-local-file-inclusion/
