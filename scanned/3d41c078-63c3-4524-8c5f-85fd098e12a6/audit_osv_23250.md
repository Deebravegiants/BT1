# [H] Arbitrary file access in KodExplorer

## Summary
Severity: High
Advisory: CVE-2022-46154
Aliases: GHSA-6f8p-4w5q-j5j2
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-12-06
Source: https://osv.dev/vulnerability/CVE-2022-46154
Type: osv

## Details
Kodexplorer is a chinese language web based file manager and browser based code editor. Versions prior to 4.50 did not prevent unauthenticated users from requesting arbitrary files from the host OS file system. As a result any files available to the host process may be accessed by arbitrary users. This issue has been addressed in version 4.50. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46154.json
- https://github.com/kalcaddle/KodExplorer/security/advisories/GHSA-6f8p-4w5q-j5j2
- https://nvd.nist.gov/vuln/detail/CVE-2022-46154
- https://github.com/kalcaddle/KodExplorer/commit/1f7072c0e12150686f10ee8cda82c004f04be98c
