# [C] ksmbd: fix slab-use-after-free in ksmbd_smb2_session_create

## Summary
Severity: Critical
Advisory: CVE-2024-50286
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50286
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix slab-use-after-free in ksmbd_smb2_session_create

There is a race condition between ksmbd_smb2_session_create and
ksmbd_expire_session. This patch add missing sessions_table_lock
while adding/deleting session from global session table.

## References
- https://git.kernel.org/stable/c/0a77715db22611df50b178374c51e2ba0d58866e
- https://git.kernel.org/stable/c/e7a2ad2044377853cf8c59528dac808a08a99c72
- https://git.kernel.org/stable/c/e923503a56b3385b64ae492e3225e4623f560c5b
- https://git.kernel.org/stable/c/f56446ba5378d19e31040b548a14ee9a8f1500ea
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50286.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
