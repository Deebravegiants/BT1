# [C] RDMA/bnxt_re: Avoid repeated requests to allocate WC pages

## Summary
Severity: Critical
Advisory: CVE-2026-72495
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72495
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Avoid repeated requests to allocate WC pages

Applications can request multiple WC pages for the same ucontext.
As of now, only 1 WC page per ucontext is supported. Add a lock to
avoid concurrent access and a check to fail repeated requests.
Also, if the mmap entry insert fails for the WC, free the Doorbell
page index mapped for the WC page.

## References
- https://git.kernel.org/stable/c/441baa79043431807115fd030d7d0bb14ed441a0
- https://git.kernel.org/stable/c/478c4d24193fe3e6aa2accd4874ae43000e4a217
- https://git.kernel.org/stable/c/da406b8b49c1dfe661a497483940d7ee781430db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72495.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72495
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
