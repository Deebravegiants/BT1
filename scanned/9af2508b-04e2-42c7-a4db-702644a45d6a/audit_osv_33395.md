# [H] mm/secretmem: fix use-after-free race in fault handler

## Summary
Severity: High
Advisory: CVE-2025-40272
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40272
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/secretmem: fix use-after-free race in fault handler

When a page fault occurs in a secret memory file created with
`memfd_secret(2)`, the kernel will allocate a new folio for it, mark the
underlying page as not-present in the direct map, and add it to the file
mapping.

If two tasks cause a fault in the same page concurrently, both could end
up allocating a folio and removing the page from the direct map, but only
one would succeed in adding the folio to the file mapping.  The task that
failed undoes the effects of its attempt by (a) freeing the folio again
and (b) putting the page back into the direct map.  However, by doing
these two operations in this order, the page becomes available to the
allocator again before it is placed back in the direct mapping.

If another task attempts to allocate the page between (a) and (b), and the
kernel tries to access it via the direct map, it would result in a
supervisor not-present page fault.

Fix the ordering to restore the direct map before the folio is freed.

## References
- https://git.kernel.org/stable/c/1e4643d6628edf9c0047b1f8f5bc574665025acb
- https://git.kernel.org/stable/c/42d486d35a4143cc37fc72ee66edc99d942dd367
- https://git.kernel.org/stable/c/4444767e625da46009fc94a453fd1967b80ba047
- https://git.kernel.org/stable/c/52f2d5cf33de9a8f5e72bbb0ed38282ae0bc4649
- https://git.kernel.org/stable/c/6f86d0534fddfbd08687fa0f01479d4226bc3c3d
- https://git.kernel.org/stable/c/bb1c19636aedae39360e6fdbcaef4f2bcff25785
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40272.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40272
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
