# [C] crypto: hisilicon/sec2 - prevent req used-after-free for sec

## Summary
Severity: Critical
Advisory: CVE-2026-53055
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53055
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: hisilicon/sec2 - prevent req used-after-free for sec

During packet transmission, if the system is under heavy load,
the hardware might complete processing the packet and free the
request memory (req) before the transmission function finishes.
If the software subsequently accesses this req, a use-after-free
error will occur. The qp_ctx memory exists throughout the packet
sending process, so replace the req with the qp_ctx.

## References
- https://git.kernel.org/stable/c/67b53a660e6bf0da2fa8d8872e897a14d8059eaf
- https://git.kernel.org/stable/c/ad73563f3a1edbfddf2724136c6a15826b354e18
- https://git.kernel.org/stable/c/b375c3c7209cc59e40e97998aa9bc768369cca0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53055.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53055
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
