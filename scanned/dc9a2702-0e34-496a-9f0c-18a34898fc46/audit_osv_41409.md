# [C] Horde VFS < 3.0.1 OS Command Injection via Horde_Vfs_Smb Driver

## Summary
Severity: Critical
Advisory: CVE-2026-60102
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-60102
Type: osv

## Details
Horde Virtual File System (VFS) API before 3.0.1 contains an OS command injection vulnerability in the Horde_Vfs_Smb driver where the _escapeShellCommand() method fails to sanitize command substitution sequences, allowing authenticated attackers to inject arbitrary shell commands through user-controlled filenames. Attackers can supply malicious filenames containing unescaped command substitution payloads through operations such as file upload, folder creation, rename, or deletion, which are interpolated into a double-quoted shell context and executed via proc_open() through /bin/sh -c before smbclient runs, resulting in arbitrary command execution on the underlying system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60102.json
- https://github.com/horde/Vfs/releases/tag/v3.0.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-60102
- https://www.vulncheck.com/advisories/horde-vfs-os-command-injection-via-horde-vfs-smb-driver
- https://github.com/horde/Vfs/pull/10
- https://github.com/horde/Vfs/commit/41f74b4acfc144e09013d04dd121e0a5da808361
- https://github.com/horde/Vfs
