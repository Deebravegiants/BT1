# [C] OPNsense: RCE on user managment

## Summary
Severity: Critical
Advisory: CVE-2026-44194
Aliases: GHSA-f59w-m967-9rf6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44194
Type: osv

## Details
OPNsense is a FreeBSD based firewall and routing platform. Prior to 26.1.8, an authenticated Remote Code Execution (RCE) vulnerability in the OPNsense core allows a user with user-management privileges to execute arbitrary system commands as root. An attacker can bypass input validation by formatting their malicious payload as a compliant email address, allowing shell commands to reach the underlying operating system. The flaw exists in the local user synchronization flow, within core/src/opnsense/scripts/auth/sync_user.php. This vulnerability is fixed in 26.1.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44194.json
- https://github.com/opnsense/core/security/advisories/GHSA-f59w-m967-9rf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-44194
