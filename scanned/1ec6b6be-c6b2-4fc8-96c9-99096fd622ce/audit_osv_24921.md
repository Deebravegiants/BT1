# [M] Dataease file upload interface does not verify permission or file type

## Summary
Severity: Medium
Advisory: CVE-2023-28435
Aliases: GHSA-625h-q3g9-rffc
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2023-28435
Type: osv

## Details
Dataease is an open source data visualization and analysis tool. The permissions for the file upload interface is not checked so users who are not logged in can upload directly to the background. The file type also goes unchecked, users could upload any type of file. These vulnerabilities has been fixed in version 1.18.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28435.json
- https://github.com/dataease/dataease/security/advisories/GHSA-625h-q3g9-rffc
- https://nvd.nist.gov/vuln/detail/CVE-2023-28435
- https://github.com/dataease/dataease/issues/4798
