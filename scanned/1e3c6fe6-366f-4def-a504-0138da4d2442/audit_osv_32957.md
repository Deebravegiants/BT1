# [H] perf: Fix sample vs do_exit()

## Summary
Severity: High
Advisory: CVE-2025-38424
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38424
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Fix sample vs do_exit()

Baisheng Gao reported an ARM64 crash, which Mark decoded as being a
synchronous external abort -- most likely due to trying to access
MMIO in bad ways.

The crash further shows perf trying to do a user stack sample while in
exit_mmap()'s tlb_finish_mmu() -- i.e. while tearing down the address
space it is trying to access.

It turns out that we stop perf after we tear down the userspace mm; a
receipie for disaster, since perf likes to access userspace for
various reasons.

Flip this order by moving up where we stop perf in do_exit().

Additionally, harden PERF_SAMPLE_CALLCHAIN and PERF_SAMPLE_STACK_USER
to abort when the current task does not have an mm (exit_mm() makes
sure to set current->mm = NULL; before commencing with the actual
teardown). Such that CPU wide events don't trip on this same problem.

## References
- https://git.kernel.org/stable/c/2ee6044a693735396bb47eeaba1ac3ae26c1c99b
- https://git.kernel.org/stable/c/456019adaa2f5366b89c868dea9b483179bece54
- https://git.kernel.org/stable/c/4f6fc782128355931527cefe3eb45338abd8ab39
- https://git.kernel.org/stable/c/507c9a595bad3abd107c6a8857d7fd125d89f386
- https://git.kernel.org/stable/c/7311970d07c4606362081250da95f2c7901fc0db
- https://git.kernel.org/stable/c/7b8f3c72175c6a63a95cf2e219f8b78e2baad34e
- https://git.kernel.org/stable/c/975ffddfa2e19823c719459d2364fcaa17673964
- https://git.kernel.org/stable/c/a9f6aab7910a0ef2895797f15c947f6d1053160f
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38424.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38424
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
