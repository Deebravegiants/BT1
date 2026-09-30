# [H] sched: sch_cake: add bounds checks to host bulk flow fairness counts

## Summary
Severity: High
Advisory: CVE-2025-21647
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2025-21647
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched: sch_cake: add bounds checks to host bulk flow fairness counts

Even though we fixed a logic error in the commit cited below, syzbot
still managed to trigger an underflow of the per-host bulk flow
counters, leading to an out of bounds memory access.

To avoid any such logic errors causing out of bounds memory accesses,
this commit factors out all accesses to the per-host bulk flow counters
to a series of helpers that perform bounds-checking before any
increments and decrements. This also has the benefit of improving
readability by moving the conditional checks for the flow mode into
these helpers, instead of having them spread out throughout the
code (which was the cause of the original logic error).

As part of this change, the flow quantum calculation is consolidated
into a helper function, which means that the dithering applied to the
ost load scaling is now applied both in the DRR rotation and when a
sparse flow's quantum is first initiated. The only user-visible effect
of this is that the maximum packet size that can be sent while a flow
stays sparse will now vary with +/- one byte in some cases. This should
not make a noticeable difference in practice, and thus it's not worth
complicating the code to preserve the old behaviour.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-503939.html
- https://git.kernel.org/stable/c/27202e2e8721c3b23831563c36ed5ac7818641ba
- https://git.kernel.org/stable/c/44fe1efb4961c1a5ccab16bb579dfc6b308ad58b
- https://git.kernel.org/stable/c/737d4d91d35b5f7fa5bb442651472277318b0bfd
- https://git.kernel.org/stable/c/91bb18950b88f955838ec0c1d97f74d135756dc7
- https://git.kernel.org/stable/c/a777e06dfc72bed73c05dcb437d7c27ad5f90f3f
- https://git.kernel.org/stable/c/b1a1743aaa4906c41c426eda97e2e2586f79246d
- https://git.kernel.org/stable/c/bb0245fa72b783cb23a9949c5048781341e91423
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21647.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21647
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
