# [C] Combodo iTop: Remote code execution using external auth variable value

## Summary
Severity: Critical
Advisory: CVE-2026-39975
Aliases: GHSA-h823-537c-xwfh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-39975
Type: osv

## Details
Combodo iTop is a web-based IT service management tool. Prior to 3.2.3, unauthenticated users could delete the .readonly file on iTop instances, leading to code execution. This file, created during the setup process, prevents users from performing write actions. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39975.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-h823-537c-xwfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-39975
