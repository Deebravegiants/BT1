# [M] sysctl: Fix data-races in proc_dou8vec_minmax().

## Summary
Severity: Medium
Advisory: CVE-2022-49634
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49634
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sysctl: Fix data-races in proc_dou8vec_minmax().

A sysctl variable is accessed concurrently, and there is always a chance
of data-race.  So, all readers and writers need some basic protection to
avoid load/store-tearing.

This patch changes proc_dou8vec_minmax() to use READ_ONCE() and
WRITE_ONCE() internally to fix data-races on the sysctl side.  For now,
proc_dou8vec_minmax() itself is tolerant to a data-race, but we still
need to add annotations on the other subsystem's side.

## References
- https://git.kernel.org/stable/c/5f776daef0b5354615ec4b4234cd9539ca05f273
- https://git.kernel.org/stable/c/7dee5d7747a69aa2be41f04c6a7ecfe3ac8cdf18
- https://git.kernel.org/stable/c/e58b02e445463065b4078bf621561da75197853f
- https://git.kernel.org/stable/c/f177b382c33900d0e5a9766493c11a1074076f78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49634.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49634
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
