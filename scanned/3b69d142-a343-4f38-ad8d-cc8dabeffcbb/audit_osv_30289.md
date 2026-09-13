# [C] ksmbd: fix slab-use-after-free in smb3_preauth_hash_rsp

## Summary
Severity: Critical
Advisory: CVE-2024-50283
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50283
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.174, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix slab-use-after-free in smb3_preauth_hash_rsp

ksmbd_user_session_put should be called under smb3_preauth_hash_rsp().
It will avoid freeing session before calling smb3_preauth_hash_rsp().

## References
- https://git.kernel.org/stable/c/1b6ad475d4ed577d34e0157eb507be00c588bf5c
- https://git.kernel.org/stable/c/b8fc56fbca7482c1e5c0e3351c6ae78982e25ada
- https://git.kernel.org/stable/c/c6cdc08c25a868a08068dfc319fa9fce982b8e7f
- https://git.kernel.org/stable/c/cb645064e0811053c94e86677f2e58ed29359d62
- https://git.kernel.org/stable/c/f7557bbca40d4ca8bb1c6c940ac6c95078bd0827
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50283.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50283
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
