# [M] sysctl: Fix data races in proc_douintvec_minmax().

## Summary
Severity: Medium
Advisory: CVE-2022-49640
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49640
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sysctl: Fix data races in proc_douintvec_minmax().

A sysctl variable is accessed concurrently, and there is always a chance
of data-race.  So, all readers and writers need some basic protection to
avoid load/store-tearing.

This patch changes proc_douintvec_minmax() to use READ_ONCE() and
WRITE_ONCE() internally to fix data-races on the sysctl side.  For now,
proc_douintvec_minmax() itself is tolerant to a data-race, but we still
need to add annotations on the other subsystem's side.

## References
- https://git.kernel.org/stable/c/2d3b559df3ed39258737789aae2ae7973d205bc1
- https://git.kernel.org/stable/c/40e0477a7371d101c55b69d9c32a7a1ed82ab5ea
- https://git.kernel.org/stable/c/b60eddf98b9716651069dfda296c91311a7a6293
- https://git.kernel.org/stable/c/e3a2144b3b6bf9ecafd91087c8b8b48171ec19df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49640.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49640
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
