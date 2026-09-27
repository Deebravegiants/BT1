# [M] ipv4: Fix a data-race around sysctl_fib_multipath_use_neigh.

## Summary
Severity: Medium
Advisory: CVE-2022-49580
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49580
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: Fix a data-race around sysctl_fib_multipath_use_neigh.

While reading sysctl_fib_multipath_use_neigh, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/14e996577ed2799a1ed6ffeb71c76d63acb28444
- https://git.kernel.org/stable/c/6727f39e99e0f545d815edebb6c94228485427ec
- https://git.kernel.org/stable/c/87507bcb4f5de16bb419e9509d874f4db6c0ad0f
- https://git.kernel.org/stable/c/b8d345db03b4deffb4f04219a51d3b1e94171b76
- https://git.kernel.org/stable/c/e045d672ba06e1d35bacb56374d350de0ac99066
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49580.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
