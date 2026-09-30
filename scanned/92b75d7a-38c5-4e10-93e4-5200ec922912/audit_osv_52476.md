# [M] CVE-2021-47491

## Summary
Severity: Medium
Advisory: CVE-2021-47491
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47491
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: khugepaged: skip huge page collapse for special files

The read-only THP for filesystems will collapse THP for files opened
readonly and mapped with VM_EXEC.  The intended usecase is to avoid TLB
misses for large text segments.  But it doesn't restrict the file types
so a THP could be collapsed for a non-regular file, for example, block
device, if it is opened readonly and mapped with EXEC permission.  This
may cause bugs, like [1] and [2].

This is definitely not the intended usecase, so just collapse THP for
regular files in order to close the attack surface.

[shy828301@gmail.com: fix vm_file check [3]]

## References
- https://git.kernel.org/stable/c/5fcb6fce74ffa614d964667110cf1a516c48c6d9
- https://git.kernel.org/stable/c/6d67b2a73b8e3a079c355bab3c1aef7d85a044b8
- https://git.kernel.org/stable/c/a4aeaa06d45e90f9b279f0b09de84bd00006e733
