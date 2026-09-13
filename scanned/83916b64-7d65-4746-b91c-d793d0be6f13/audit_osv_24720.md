# [H] Improper access control to download file in metersphere

## Summary
Severity: High
Advisory: CVE-2023-25573
Aliases: GHSA-mcwr-j9vm-5g8h
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-03-09
Source: https://osv.dev/vulnerability/CVE-2023-25573
Type: osv

## Details
metersphere is an open source continuous testing platform. In affected versions an improper access control vulnerability exists in `/api/jmeter/download/files`, which allows any user to download any file without authentication. This issue may expose all files available to the running process. This issue has been addressed in version 1.20.20 lts and 2.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25573.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-mcwr-j9vm-5g8h
- https://nvd.nist.gov/vuln/detail/CVE-2023-25573
