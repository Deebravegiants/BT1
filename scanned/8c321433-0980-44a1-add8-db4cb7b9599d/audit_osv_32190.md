# [M] CVE-2025-25478

## Summary
Severity: Medium
Advisory: CVE-2025-25478
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-02-28
Source: https://osv.dev/vulnerability/CVE-2025-25478
Type: osv

## Details
The account file upload functionality in Syspass 3.2.x fails to properly handle special characters in filenames. This mismanagement leads to the disclosure of the web application s source code, exposing sensitive information such as the database password.

## References
- https://github.com/sysentr0py/CVEs/tree/main/CVE-2025-25478
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25478.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25478
