# [M] ALPINE-CVE-2026-24049

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-24049
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-24049
Type: osv

## Affected
- Alpine:v3.22: `py3-wheel` — affected >=0.40.0 <0.46.3-r0
- Alpine:v3.23: `py3-wheel` — affected >=0.40.0 <0.46.3-r0
- Alpine:v3.24: `py3-wheel` — affected >=0.40.0 <0.46.3-r0

## Details
wheel is a command line tool for manipulating Python wheel files, as defined in PEP 427. In versions 0.40.0 through 0.46.1, the unpack function is vulnerable to file permission modification through mishandling of file permissions after extraction. The logic blindly trusts the filename from the archive header for the chmod operation, even though the extraction process itself might have sanitized the path. Attackers can craft a malicious wheel file that, when unpacked, changes the permissions of critical system files (e.g., /etc/passwd, SSH keys, config files), allowing for Privilege Escalation or arbitrary code execution by modifying now-writable scripts. This issue has been fixed in version 0.46.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-24049
