# [H] perf/aux: Fix AUX buffer serialization

## Summary
Severity: High
Advisory: CVE-2024-46713
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46713
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/aux: Fix AUX buffer serialization

Ole reported that event->mmap_mutex is strictly insufficient to
serialize the AUX buffer, add a per RB mutex to fully serialize it.

Note that in the lock order comment the perf_event::mmap_mutex order
was already wrong, that is, it nesting under mmap_lock is not new with
this patch.

## References
- https://git.kernel.org/stable/c/2ab9d830262c132ab5db2f571003d80850d56b2a
- https://git.kernel.org/stable/c/52d13d224fdf1299c8b642807fa1ea14d693f5ff
- https://git.kernel.org/stable/c/7882923f1cb88dc1a17f2bf0c81b1fc80d44db82
- https://git.kernel.org/stable/c/9dc7ad2b67772cfb94ceb3b0c9c4023c2463215d
- https://git.kernel.org/stable/c/b9b6882e243b653d379abbeaa64a500182aba370
- https://git.kernel.org/stable/c/c4b69bee3f4ef76809288fe6827bc14d4ae788ef
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46713.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46713
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
