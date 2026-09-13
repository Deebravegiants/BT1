# [M] ipv6: Fix memleak of nhc_pcpu_rth_output in fib_check_nh_v6_gw().

## Summary
Severity: Medium
Advisory: CVE-2025-22005
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22005
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: Fix memleak of nhc_pcpu_rth_output in fib_check_nh_v6_gw().

fib_check_nh_v6_gw() expects that fib6_nh_init() cleans up everything
when it fails.

Commit 7dd73168e273 ("ipv6: Always allocate pcpu memory in a fib6_nh")
moved fib_nh_common_init() before alloc_percpu_gfp() within fib6_nh_init()
but forgot to add cleanup for fib6_nh->nh_common.nhc_pcpu_rth_output in
case it fails to allocate fib6_nh->rt6i_pcpu, resulting in memleak.

Let's call fib_nh_common_release() and clear nhc_pcpu_rth_output in the
error path.

Note that we can remove the fib6_nh_release() call in nh_create_ipv6()
later in net-next.git.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/119dcafe36795a15ae53351cbbd6177aaf94ffef
- https://git.kernel.org/stable/c/16267a5036173d0173377545b4b6021b081d0933
- https://git.kernel.org/stable/c/1bd12dfc058e1e68759d313d7727d68dbc1b8964
- https://git.kernel.org/stable/c/29d91820184d5cbc70f3246d4911d96eaeb930d6
- https://git.kernel.org/stable/c/596a883c4ce2d2e9c175f25b98fed3a1f33fea38
- https://git.kernel.org/stable/c/77c41cdbe6bce476e08d3251c0d501feaf10a9f3
- https://git.kernel.org/stable/c/9740890ee20e01f99ff1dde84c63dcf089fabb98
- https://git.kernel.org/stable/c/d3d5b4b5ae263c3225db363ba08b937e2e2b0380
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22005.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22005
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
