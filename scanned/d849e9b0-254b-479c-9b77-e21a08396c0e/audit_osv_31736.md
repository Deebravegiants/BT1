# [H] gfs2: Truncate address space when flipping GFS2_DIF_JDATA flag

## Summary
Severity: High
Advisory: CVE-2025-21699
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-21699
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.234, >=5.11.0 <5.15.178, >=5.16.0 <6.1.128, >=6.2.0 <6.6.75, >=6.7.0 <6.12.12, >=6.13.0 <6.13.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: Truncate address space when flipping GFS2_DIF_JDATA flag

Truncate an inode's address space when flipping the GFS2_DIF_JDATA flag:
depending on that flag, the pages in the address space will either use
buffer heads or iomap_folio_state structs, and we cannot mix the two.

## References
- https://git.kernel.org/stable/c/2a40a140e11fec699e128170ccaa98b6b82cb503
- https://git.kernel.org/stable/c/4516febe325342555bb09ca5b396fb816d655821
- https://git.kernel.org/stable/c/4dd57d1f0e9844311c635a7fb39abce4f2ac5a61
- https://git.kernel.org/stable/c/4e3ded34f3f3c9d7ed2aac7be8cf51153646574a
- https://git.kernel.org/stable/c/5bb1fd0855bb0abc7d97e44758d6ffed7882d2d0
- https://git.kernel.org/stable/c/7c9d9223802fbed4dee1ae301661bf346964c9d2
- https://git.kernel.org/stable/c/8c41abc11aa8438c9ed2d973f97e66674c0355df
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21699.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21699
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
