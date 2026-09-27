# [H] CVE-2022-22942

## Summary
Severity: High
Advisory: CVE-2022-22942
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2022-22942
Type: osv

## Details
The vmwgfx driver contains a local privilege escalation vulnerability that allows unprivileged users to gain access to files opened by other processes on the system through a dangling 'file' pointer.

## References
- https://github.com/vmware/photon/wiki/Security-Update-3.0-356
- https://github.com/vmware/photon/wiki/Security-Update-4.0-148
- https://www.openwall.com/lists/oss-security/2022/01/27/4
