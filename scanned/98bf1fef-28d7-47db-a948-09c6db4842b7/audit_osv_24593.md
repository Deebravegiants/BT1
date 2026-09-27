# [C] Unrestricted file upload leads to Remote Code Execution in erohtar/Dasherr

## Summary
Severity: Critical
Advisory: CVE-2023-23607
Aliases: GHSA-6rgc-2x44-7phq
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-20
Source: https://osv.dev/vulnerability/CVE-2023-23607
Type: osv

## Details
erohtar/Dasherr is a dashboard for self-hosted services. In affected versions unrestricted file upload allows any unauthenticated user to execute arbitrary code on the server. The file /www/include/filesave.php allows for any file to uploaded to anywhere. If an attacker uploads a php file they can execute code on the server. This issue has been addressed in version 1.05.00. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://www.vicarius.io/vsociety/posts/analyzing-arbitrary-file-upload-in-dasherr-cve-2023-23607-23608
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23607.json
- https://github.com/erohtar/Dasherr/security/advisories/GHSA-6rgc-2x44-7phq
- https://nvd.nist.gov/vuln/detail/CVE-2023-23607
- https://github.com/erohtar/Dasherr/commit/445325c7cf1148a8cd38af3a90789c6cbf6c5112
