# [M] sysctl: Fix data races in proc_douintvec().

## Summary
Severity: Medium
Advisory: CVE-2022-49641
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49641
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sysctl: Fix data races in proc_douintvec().

A sysctl variable is accessed concurrently, and there is always a chance
of data-race.  So, all readers and writers need some basic protection to
avoid load/store-tearing.

This patch changes proc_douintvec() to use READ_ONCE() and WRITE_ONCE()
internally to fix data-races on the sysctl side.  For now, proc_douintvec()
itself is tolerant to a data-race, but we still need to add annotations on
the other subsystem's side.

## References
- https://git.kernel.org/stable/c/4762b532ec9539755aab61445d5da6e1926ccb99
- https://git.kernel.org/stable/c/630c76850d554d7140232e71b5d1663e88cffb54
- https://git.kernel.org/stable/c/d335db59f7fb3353f56e52371f1ee796ae9c8f09
- https://git.kernel.org/stable/c/d5d54714e329f646bd7af4994fc427d88ee68936
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49641.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49641
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
