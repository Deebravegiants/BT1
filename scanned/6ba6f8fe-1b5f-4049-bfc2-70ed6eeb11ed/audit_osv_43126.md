# [C] RDMA/bnxt_re: Proper rollback if the ioremap fails

## Summary
Severity: Critical
Advisory: CVE-2026-72496
Ecosystem: Linux
CVSS: 9.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72496
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Proper rollback if the ioremap fails

bnxt_qplib_alloc_dpi returns success even if ioremap fails.
Add the proper rollback when the ioremap fails and return
-ENOMEM status.

## References
- https://git.kernel.org/stable/c/303f6fef95df5e5316970746d861cf6daeeca77f
- https://git.kernel.org/stable/c/87267803a8c824616eb147c5dad7030a5db6f878
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72496.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72496
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
