# [H] CVE-2022-34126

## Summary
Severity: High
Advisory: CVE-2022-34126
Aliases: GHSA-jcmw-hpgh-357p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2022-34126
Type: osv

## Details
The Activity plugin before 3.1.1 for GLPI allows reading local files via directory traversal in the front/cra.send.php file parameter.

## References
- https://github.com/InfotelGLPI/activity/releases/tag/3.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/34xxx/CVE-2022-34126.json
- https://github.com/InfotelGLPI/activity/security/advisories/GHSA-jcmw-hpgh-357p
- https://nvd.nist.gov/vuln/detail/CVE-2022-34126
- https://pentest.blog/advisory-glpi-service-management-software-sql-injection-remote-code-execution-and-local-file-inclusion/
