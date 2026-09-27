# [H] CVE-2020-15264

## Summary
Severity: High
Advisory: CVE-2020-15264
Aliases: GHSA-rpgx-h675-r3jf
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-20
Source: https://osv.dev/vulnerability/CVE-2020-15264
Type: osv

## Details
The Boxstarter installer before version 2.13.0 configures C:\ProgramData\Boxstarter to be in the system-wide PATH environment variable. However, this directory is writable by normal, unprivileged users. To exploit the vulnerability, place a DLL in this directory that a privileged service is looking for. For example, WptsExtensions.dll When Windows starts, it'll execute the code in DllMain() with SYSTEM privileges. Any unprivileged user can execute code with SYSTEM privileges. The issue is fixed in version 3.13.0

## References
- https://github.com/chocolatey/boxstarter/security/advisories/GHSA-rpgx-h675-r3jf
- https://www.kb.cert.org/vuls/id/208577
- https://github.com/chocolatey/boxstarter/commit/67e320491813550b48900e87105a34ceefdcf633
