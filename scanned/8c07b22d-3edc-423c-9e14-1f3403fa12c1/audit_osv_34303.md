# [C] StreamVault can perform remote command execution

## Summary
Severity: Critical
Advisory: CVE-2025-57799
Aliases: GHSA-qg4r-92hv-g9f4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-09-01
Source: https://osv.dev/vulnerability/CVE-2025-57799
Type: osv

## Details
StreamVault is a multi-platform video parsing and downloading tool. Prior to version 250822, after logging into the StreamVault-system, an attacker can modify certain system parameters, construct malicious commands, execute command injection attacks against the system, and ultimately gain server privileges. Users of all versions of the StreamVault system to date who have not modified their background passwords or use weak passwords are at risk of having their systems taken over via remote command execution. This issue has been patched in version 250822.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57799.json
- https://github.com/lemon8866/StreamVault/security/advisories/GHSA-qg4r-92hv-g9f4
- https://nvd.nist.gov/vuln/detail/CVE-2025-57799
- https://github.com/lemon8866/StreamVault/commit/2e3f1f54b7d8a4e6389b640796866ac1108780ef
