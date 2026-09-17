# [H] ipv6: fix a BUG in rt6_get_pcpu_route() under PREEMPT_RT

## Summary
Severity: High
Advisory: CVE-2025-71080
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71080
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix a BUG in rt6_get_pcpu_route() under PREEMPT_RT

On PREEMPT_RT kernels, after rt6_get_pcpu_route() returns NULL, the
current task can be preempted. Another task running on the same CPU
may then execute rt6_make_pcpu_route() and successfully install a
pcpu_rt entry. When the first task resumes execution, its cmpxchg()
in rt6_make_pcpu_route() will fail because rt6i_pcpu is no longer
NULL, triggering the BUG_ON(prev). It's easy to reproduce it by adding
mdelay() after rt6_get_pcpu_route().

Using preempt_disable/enable is not appropriate here because
ip6_rt_pcpu_alloc() may sleep.

Fix this by handling the cmpxchg() failure gracefully on PREEMPT_RT:
free our allocation and return the existing pcpu_rt installed by
another task. The BUG_ON is replaced by WARN_ON_ONCE for non-PREEMPT_RT
kernels where such races should not occur.

## References
- https://git.kernel.org/stable/c/1adaea51c61b52e24e7ab38f7d3eba023b2d050d
- https://git.kernel.org/stable/c/1dc33ad0867325f8d2c6d7b2a6f542d4f3121f66
- https://git.kernel.org/stable/c/787515ccb2292f82eb0876993129154629a49651
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71080.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
