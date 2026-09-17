# [H] RDMA/bnxt_re: Add sanity checks on rdev validity

## Summary
Severity: High
Advisory: CVE-2025-21901
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21901
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.18, >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Add sanity checks on rdev validity

There is a possibility that ulp_irq_stop and ulp_irq_start
callbacks will be called when the device is in detached state.
This can cause a crash due to NULL pointer dereference as
the rdev is already freed.

## References
- https://git.kernel.org/stable/c/8cb0eef46d70a99c88c26a1addb7fd955242e0e6
- https://git.kernel.org/stable/c/aed1bc673907e3df372b317c10ff2f3582f8bf1a
- https://git.kernel.org/stable/c/f0df225d12fcb049429fb5bf5122afe143c2dd15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21901.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21901
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
