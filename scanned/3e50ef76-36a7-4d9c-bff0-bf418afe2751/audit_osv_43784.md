# [C] NFS: Pin the 'struct nfs_server' during a FREE_STATEID call

## Summary
Severity: Critical
Advisory: CVE-2026-74730
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74730
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Pin the 'struct nfs_server' during a FREE_STATEID call

Dan Aloni reports that he was able to hit a use-after-free bug if a
FREE_STATEID operation gets delayed for whatever reason. Fix this by
bumping the refcount of the 'struct nfs_server' object for the duration
of the FREE_STATEID so it doesn't get cleaned up from underneath us
while operations are still in flight.

## References
- https://git.kernel.org/stable/c/80ed3d762628b36c9e4b22fac7c65b72ef3b13dd
- https://git.kernel.org/stable/c/af62f1af182d33a0de38308c012841885d8ab92e
- https://git.kernel.org/stable/c/caee6a68ffaa5016dfc01cd0b3dc1896a32e3abd
- https://git.kernel.org/stable/c/cf616096a0f3a2b60f7d68b6b39674a6867ded9c
- https://git.kernel.org/stable/c/d71dfffa512e71b166a889484e4c3b148a9a3af2
- https://git.kernel.org/stable/c/d858ab09e787106432d4d9830bad9dfedf02f890
- https://git.kernel.org/stable/c/ed1161ab6239761958b38d5667225634fc2be894
- https://git.kernel.org/stable/c/ed2f92ce2fc48463c41e0e540b9a3454889e8af8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74730.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
