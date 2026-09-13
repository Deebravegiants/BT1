# [C] ksmbd: fix user-after-free from session log off

## Summary
Severity: Critical
Advisory: CVE-2024-50086
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50086
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.171, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix user-after-free from session log off

There is racy issue between smb2 session log off and smb2 session setup.
It will cause user-after-free from session log off.
This add session_lock when setting SMB2_SESSION_EXPIRED and referece
count to session struct not to free session while it is being used.

## References
- https://git.kernel.org/stable/c/0f62358ce85b2d4c949ef1b648be01b29cec667a
- https://git.kernel.org/stable/c/5511999e9615e4318e9142d23b29bd1597befc08
- https://git.kernel.org/stable/c/7aa8804c0b67b3cb263a472d17f2cb50d7f1a930
- https://git.kernel.org/stable/c/a9839c37fd813b432988f58a9d9dd59253d3eb2c
- https://git.kernel.org/stable/c/ee371898b53a9b9b51c02d22a8c31bfb86d45f0d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50086.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50086
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
