# [H] RDMA/bnxt_re: Free CQ toggle page after firmware teardown

## Summary
Severity: High
Advisory: CVE-2026-72499
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72499
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Free CQ toggle page after firmware teardown

Free the toggle page only after firmware teardown completes so that
an NQ interrupt arriving during bnxt_qplib_destroy_cq() won't write
the toggle value to an already-freed page. Move free_page() after
bnxt_qplib_destroy_cq.

## References
- https://git.kernel.org/stable/c/b193854675ecad43b4d69c304c1b6a90b206cc99
- https://git.kernel.org/stable/c/bb45e06f9914ca64ac95341a80a0c20bb8dd46a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72499.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72499
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
