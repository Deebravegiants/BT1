# [M] i2c: designware: use casting of u64 in clock multiplication to avoid overflow

## Summary
Severity: Medium
Advisory: CVE-2022-49749
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49749
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: designware: use casting of u64 in clock multiplication to avoid overflow

In functions i2c_dw_scl_lcnt() and i2c_dw_scl_hcnt() may have overflow
by depending on the values of the given parameters including the ic_clk.
For example in our use case where ic_clk is larger than one million,
multiplication of ic_clk * 4700 will result in 32 bit overflow.

Add cast of u64 to the calculation to avoid multiplication overflow, and
use the corresponding define for divide.

## References
- https://git.kernel.org/stable/c/2f29d780bd691d20e89e5b35d5e6568607115e94
- https://git.kernel.org/stable/c/9f36aae9e80e79b7a6d62227eaa96935166be9fe
- https://git.kernel.org/stable/c/c8c37bc514514999e62a17e95160ed9ebf75ca8d
- https://git.kernel.org/stable/c/ed173f77fd28a3e4fffc13b3f28687b9eba61157
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49749.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49749
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
