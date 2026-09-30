# [H] cachefiles: add missing lock protection when polling

## Summary
Severity: High
Advisory: CVE-2024-42250
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42250
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

cachefiles: add missing lock protection when polling

Add missing lock protection in poll routine when iterating xarray,
otherwise:

Even with RCU read lock held, only the slot of the radix tree is
ensured to be pinned there, while the data structure (e.g. struct
cachefiles_req) stored in the slot has no such guarantee.  The poll
routine will iterate the radix tree and dereference cachefiles_req
accordingly.  Thus RCU read lock is not adequate in this case and
spinlock is needed here.

## References
- https://git.kernel.org/stable/c/6bb6bd3dd6f382dfd36220d4b210a0c77c066651
- https://git.kernel.org/stable/c/8eadcab7f3dd809edbe5ae20533ff843dfea3a07
- https://git.kernel.org/stable/c/97cfd5e20ddc2e33e16ce369626ce76c9a475fd7
- https://git.kernel.org/stable/c/cf5bb09e742a9cf6349127e868329a8f69b7a014
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42250.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42250
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
