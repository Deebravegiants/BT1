# [M] clk: zynq: Prevent null pointer dereference caused by kmalloc failure

## Summary
Severity: Medium
Advisory: CVE-2024-27037
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27037
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: zynq: Prevent null pointer dereference caused by kmalloc failure

The kmalloc() in zynq_clk_setup() will return null if the
physical memory has run out. As a result, if we use snprintf()
to write data to the null address, the null pointer dereference
bug will happen.

This patch uses a stack variable to replace the kmalloc().

## References
- https://git.kernel.org/stable/c/01511ac7be8e45f80e637f6bf61af2d3d2dee9db
- https://git.kernel.org/stable/c/0801c893fd48cdba66a3c8f44c3fe43cc67d3b85
- https://git.kernel.org/stable/c/58a946ab43501f2eba058d24d96af0ad1122475b
- https://git.kernel.org/stable/c/7938e9ce39d6779d2f85d822cc930f73420e54a6
- https://git.kernel.org/stable/c/8c4889a9ea861d7be37463c10846eb75e1b49c9d
- https://git.kernel.org/stable/c/ca976c6a592f789700200069ef9052493c0b73d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27037.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27037
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
