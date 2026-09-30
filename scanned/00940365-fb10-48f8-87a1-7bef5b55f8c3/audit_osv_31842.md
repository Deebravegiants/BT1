# [H] io_uring: prevent opcode speculation

## Summary
Severity: High
Advisory: CVE-2025-21863
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21863
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.259, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: prevent opcode speculation

sqe->opcode is used for different tables, make sure we santitise it
against speculations.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/18eae8420081ef8e043ad455937bfb470ef08607
- https://git.kernel.org/stable/c/1e988c3fe1264708f4f92109203ac5b1d65de50b
- https://git.kernel.org/stable/c/506b9b5e8c2d2a411ea8fe361333f5081c56d23a
- https://git.kernel.org/stable/c/87e9eef43c758da267f6332678058a79764c7eba
- https://git.kernel.org/stable/c/b9826e3b26ec031e9063f64a7c735449c43955e4
- https://git.kernel.org/stable/c/d261ead565a080e3411b0dd04e6d58a52471cac8
- https://git.kernel.org/stable/c/fdbfd52bd8b85ed6783365ff54c82ab7067bd61b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21863.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21863
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
