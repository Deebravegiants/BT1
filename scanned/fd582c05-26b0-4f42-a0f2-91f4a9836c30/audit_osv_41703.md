# [H] FileGator privilege escalation

## Summary
Severity: High
Advisory: CVE-2026-63358
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-63358
Type: osv

## Details
FileGator accepts arbitrary Unix permission values via the '/chmoditems' API endpoint and passes the value directly to PHP's native 'chmod()' function through 'octdec()' conversion, with no validation. This allows an authenticated user with 'chmod' permission to upgrade their privileges to root.

## References
- https://github.com/filegator/filegator/tree/master
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63358.json
- https://github.com/filegator/filegator/blob/master/CHANGELOG.md#7142---2026-05-18
- https://nvd.nist.gov/vuln/detail/CVE-2026-63358
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2026/va-26-202-03.json
- https://www.cve.org/CVERecord?id=CVE-2026-63358
- https://github.com/filegator/filegator/commit/4a44ed9a43f84505703dce669c68fb55270c3f2c
