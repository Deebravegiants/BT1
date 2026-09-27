# [H] Arbitrary File Read Vulnerability in metersphere

## Summary
Severity: High
Advisory: CVE-2023-25814
Aliases: GHSA-fwc3-5h55-mh2j
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2023-03-09
Source: https://osv.dev/vulnerability/CVE-2023-25814
Type: osv

## Details
metersphere is an open source continuous testing platform. In versions prior to 2.7.1 a user who has permission to create a resource file through UI operations is able to append a path to their submission query which will be read by the system and displayed to the user. This allows a users of the system to read arbitrary files on the filesystem of the server so long as the server process itself has permission to read the requested files. This issue has been addressed in version 2.7.1. All users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25814.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-fwc3-5h55-mh2j
- https://nvd.nist.gov/vuln/detail/CVE-2023-25814
