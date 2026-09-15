# [H] mm: revert "mm: shmem: fix data-race in shmem_getattr()"

## Summary
Severity: High
Advisory: CVE-2024-53136
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53136
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.323 <4.19.325, >=5.4.285 <5.4.287, >=5.10.229 <5.10.231, >=5.15.171 <5.15.174, >=6.1.116 <6.1.119, >=6.6.60 <6.6.63, >=6.11.7 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: revert "mm: shmem: fix data-race in shmem_getattr()"

Revert d949d1d14fa2 ("mm: shmem: fix data-race in shmem_getattr()") as
suggested by Chuck [1].  It is causing deadlocks when accessing tmpfs over
NFS.

As Hugh commented, "added just to silence a syzbot sanitizer splat: added
where there has never been any practical problem".

## References
- https://git.kernel.org/stable/c/36b537e8f302f670c7cf35d88a3a294443e32d52
- https://git.kernel.org/stable/c/57cc8d253099d1b8627f0fb487ee011d9158ccc9
- https://git.kernel.org/stable/c/5874c1150e77296565ad6e495ef41fbf87570d14
- https://git.kernel.org/stable/c/64e67e8694252c1bf01b802ee911be3fee62c36b
- https://git.kernel.org/stable/c/901dc2ad7c3789fa87dc3956f6697c5d62d5cf7e
- https://git.kernel.org/stable/c/a3c65022d89d5baa2cea8e87a6de983ea305f14c
- https://git.kernel.org/stable/c/d1aa0c04294e29883d65eac6c2f72fe95cc7c049
- https://git.kernel.org/stable/c/d3f9d88c2c03b2646ace336236adca19f7697bd3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53136.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
