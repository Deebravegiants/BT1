# [H] spi: ti-qspi: fix use-after-free after DMA setup failure

## Summary
Severity: High
Advisory: CVE-2026-64221
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64221
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: ti-qspi: fix use-after-free after DMA setup failure

The driver falls back to PIO mode if DMA setup fails during probe.

Make sure to clear the DMA channel pointer also if buffer allocation
fails to avoid passing a pointer to the released channel to the DMA
engine (or trying to free the channel a second time on late probe errors
or driver unbind).

This issue was flagged by Sashiko when reviewing a devres allocation
conversion patch.

## References
- https://git.kernel.org/stable/c/178b9b570c0f75fa7e691490520328b20d19138e
- https://git.kernel.org/stable/c/1cd927002120678bd5d23c760246639caa53040e
- https://git.kernel.org/stable/c/3bbbe7ae3fdada0df4157c1ffe989f92dfa8dcd6
- https://git.kernel.org/stable/c/9c6f306a8140962c7284197db54b96fdb5f468d6
- https://git.kernel.org/stable/c/d6f422b122922d1abee907d673bcc990e5f3672d
- https://git.kernel.org/stable/c/d7a076fb596c7b408ed6df74793a597990a6d860
- https://git.kernel.org/stable/c/ea6ec3343e05f7937a53eb6d7617b3abdb4abc19
- https://git.kernel.org/stable/c/f2dc841d7dc9063fe9b47ced869b1271e55052ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64221.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64221
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
