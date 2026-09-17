# [H] iio: adc: ti-adc161s626: use DMA-safe memory for spi_read()

## Summary
Severity: High
Advisory: CVE-2026-31768
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31768
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ti-adc161s626: use DMA-safe memory for spi_read()

Add a DMA-safe buffer and use it for spi_read() instead of a stack
memory. All SPI buffers must be DMA-safe.

Since we only need up to 3 bytes, we just use a u8[] instead of __be16
and __be32 and change the conversion functions appropriately.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/014c6d27878d3883f7bb065610768fd021de1a96
- https://git.kernel.org/stable/c/67b3a91bdc48220bfb67155ab528121b9c822782
- https://git.kernel.org/stable/c/768461517a28d80fe81ea4d5d03a90cd184ea6ad
- https://git.kernel.org/stable/c/b3bb8faeca1a2ef7be95ee8a512b639f9ffce947
- https://git.kernel.org/stable/c/d2d031b0786ea66ab0577c9d2d71435068d32199
- https://git.kernel.org/stable/c/fa64aab25aba47296aa8d12bb4c88ec3fecb2054
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31768.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31768
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
