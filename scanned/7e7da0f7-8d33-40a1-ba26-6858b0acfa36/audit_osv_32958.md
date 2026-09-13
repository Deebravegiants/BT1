# [H] i2c: tegra: check msg length in SMBUS block read

## Summary
Severity: High
Advisory: CVE-2025-38425
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38425
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: tegra: check msg length in SMBUS block read

For SMBUS block read, do not continue to read if the message length
passed from the device is '0' or greater than the maximum allowed bytes.

## References
- https://git.kernel.org/stable/c/3f03f77ce688d02da284174e1884b6065d6159bd
- https://git.kernel.org/stable/c/75a864f21ceeb8c1e8ce1b7589174fec2c3a039e
- https://git.kernel.org/stable/c/a6e04f05ce0b070ab39d5775580e65c7d943da0b
- https://git.kernel.org/stable/c/be5f6a65509cd5675362f15eb0440fb28b0f9d64
- https://git.kernel.org/stable/c/c39d1a9ae4ad66afcecab124d7789722bfe909fa
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38425.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38425
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
