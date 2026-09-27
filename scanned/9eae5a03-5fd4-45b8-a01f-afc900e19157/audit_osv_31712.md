# [M] iomap: avoid avoid truncating 64-bit offset to 32 bits

## Summary
Severity: Medium
Advisory: CVE-2025-21667
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21667
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.127, >=6.2.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: avoid avoid truncating 64-bit offset to 32 bits

on 32-bit kernels, iomap_write_delalloc_scan() was inadvertently using a
32-bit position due to folio_next_index() returning an unsigned long.
This could lead to an infinite loop when writing to an xfs filesystem.

## References
- https://git.kernel.org/stable/c/402ce16421477e27f30b57d6d1a6dc248fa3a4e4
- https://git.kernel.org/stable/c/7ca4bd6b754913910151acce00be093f03642725
- https://git.kernel.org/stable/c/91371922704c8d82049ef7c2ad974d0a2cd1174d
- https://git.kernel.org/stable/c/c13094b894de289514d84b8db56d1f2931a0bade
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21667.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
