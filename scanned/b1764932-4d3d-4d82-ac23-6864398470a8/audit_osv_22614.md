# [M] CVE-2022-34125

## Summary
Severity: Medium
Advisory: CVE-2022-34125
Aliases: GHSA-wv59-3rv4-vm9f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2022-34125
Type: osv

## Details
front/icon.send.php in the CMDB plugin before 3.0.3 for GLPI allows attackers to gain read access to sensitive information via a _log/ pathname in the file parameter.

## References
- https://github.com/InfotelGLPI/cmdb/releases/tag/3.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/34xxx/CVE-2022-34125.json
- https://github.com/InfotelGLPI/cmdb/security/advisories/GHSA-wv59-3rv4-vm9f
- https://nvd.nist.gov/vuln/detail/CVE-2022-34125
- https://pentest.blog/advisory-glpi-service-management-software-sql-injection-remote-code-execution-and-local-file-inclusion/
