# [H] RISC-V: KVM: fix stack overrun when loading vlenb

## Summary
Severity: High
Advisory: CVE-2025-39815
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39815
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RISC-V: KVM: fix stack overrun when loading vlenb

The userspace load can put up to 2048 bits into an xlen bit stack
buffer.  We want only xlen bits, so check the size beforehand.

## References
- https://git.kernel.org/stable/c/6d28659b692a0212f360f8bd8a58712b339f9aac
- https://git.kernel.org/stable/c/799766208f09f95677a9ab111b93872d414fbad7
- https://git.kernel.org/stable/c/c76bf8359188a11f8fd790e5bbd6077894a245cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39815.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39815
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
