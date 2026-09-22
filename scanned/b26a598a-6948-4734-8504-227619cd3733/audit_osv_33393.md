# [H] mm, swap: fix potential UAF issue for VMA readahead

## Summary
Severity: High
Advisory: CVE-2025-40270
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40270
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm, swap: fix potential UAF issue for VMA readahead

Since commit 78524b05f1a3 ("mm, swap: avoid redundant swap device
pinning"), the common helper for allocating and preparing a folio in the
swap cache layer no longer tries to get a swap device reference
internally, because all callers of __read_swap_cache_async are already
holding a swap entry reference.  The repeated swap device pinning isn't
needed on the same swap device.

Caller of VMA readahead is also holding a reference to the target entry's
swap device, but VMA readahead walks the page table, so it might encounter
swap entries from other devices, and call __read_swap_cache_async on
another device without holding a reference to it.

So it is possible to cause a UAF when swapoff of device A raced with
swapin on device B, and VMA readahead tries to read swap entries from
device A.  It's not easy to trigger, but in theory, it could cause real
issues.

Make VMA readahead try to get the device reference first if the swap
device is a different one from the target entry.

## References
- https://git.kernel.org/stable/c/1c2a936edd71e133f2806e68324ec81a4eb07588
- https://git.kernel.org/stable/c/a4145be7b56bfa87dce56415c3ad993071462b8a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40270.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
