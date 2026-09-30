# [H] ASoC: Intel: avs: Fix potential RX buffer overflow

## Summary
Severity: High
Advisory: CVE-2022-50325
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50325
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: Intel: avs: Fix potential RX buffer overflow

If an event caused firmware to return invalid RX size for
LARGE_CONFIG_GET, memcpy_fromio() could end up copying too many bytes.
Fix by utilizing min_t().

## References
- https://git.kernel.org/stable/c/0bad12fee5ae16ab439d97c66c4238f5f4cc7f68
- https://git.kernel.org/stable/c/23ae34e033b2c0e5e88237af82b163b296fd6aa9
- https://git.kernel.org/stable/c/ec1f0c12cb2e614c3fa8e9402f7ffcf82166078a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50325.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50325
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
