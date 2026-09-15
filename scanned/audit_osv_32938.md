# [H] rose: fix dangling neighbour pointers in rose_rt_device_down()

## Summary
Severity: High
Advisory: CVE-2025-38377
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38377
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.187, >=5.16.0 <6.1.144, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rose: fix dangling neighbour pointers in rose_rt_device_down()

There are two bugs in rose_rt_device_down() that can cause
use-after-free:

1. The loop bound `t->count` is modified within the loop, which can
   cause the loop to terminate early and miss some entries.

2. When removing an entry from the neighbour array, the subsequent entries
   are moved up to fill the gap, but the loop index `i` is still
   incremented, causing the next entry to be skipped.

For example, if a node has three neighbours (A, A, B) with count=3 and A
is being removed, the second A is not checked.

    i=0: (A, A, B) -> (A, B) with count=2
          ^ checked
    i=1: (A, B)    -> (A, B) with count=2
             ^ checked (B, not A!)
    i=2: (doesn't occur because i < count is false)

This leaves the second A in the array with count=2, but the rose_neigh
structure has been freed. Code that accesses these entries assumes that
the first `count` entries are valid pointers, causing a use-after-free
when it accesses the dangling pointer.

Fix both issues by iterating over the array in reverse order with a fixed
loop bound. This ensures that all entries are examined and that the removal
of an entry doesn't affect subsequent iterations.

## References
- https://git.kernel.org/stable/c/2b952dbb32fef835756f07ff0cd77efbb836dfea
- https://git.kernel.org/stable/c/2c6c82ee074bfcfd1bc978ec45bfea37703d840a
- https://git.kernel.org/stable/c/34a500caf48c47d5171f4aa1f237da39b07c6157
- https://git.kernel.org/stable/c/446ac00b86be1670838e513b643933d78837d8db
- https://git.kernel.org/stable/c/7a1841c9609377e989ec41c16551309ce79c39e4
- https://git.kernel.org/stable/c/94e0918e39039c47ddceb609500817f7266be756
- https://git.kernel.org/stable/c/b6b232e16e08c6dc120672b4753392df0d28c1b4
- https://git.kernel.org/stable/c/fe62a35fb1f77f494ed534fc69a9043dc5a30ce1
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38377.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38377
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
