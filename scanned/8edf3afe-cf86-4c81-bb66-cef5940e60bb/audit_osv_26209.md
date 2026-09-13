# [M] spi: sun6i: reduce DMA RX transfer width to single byte

## Summary
Severity: Medium
Advisory: CVE-2023-52511
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52511
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.134, >=5.16.0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: sun6i: reduce DMA RX transfer width to single byte

Through empirical testing it has been determined that sometimes RX SPI
transfers with DMA enabled return corrupted data. This is down to single
or even multiple bytes lost during DMA transfer from SPI peripheral to
memory. It seems the RX FIFO within the SPI peripheral can become
confused when performing bus read accesses wider than a single byte to it
during an active SPI transfer.

This patch reduces the width of individual DMA read accesses to the
RX FIFO to a single byte to mitigate that issue.

## References
- https://git.kernel.org/stable/c/171f8a49f212e87a8b04087568e1b3d132e36a18
- https://git.kernel.org/stable/c/b3c21c9c7289692f4019f163c3b06d8bdf78b355
- https://git.kernel.org/stable/c/e15bb292b24630ee832bfc7fd616bd72c7682bbb
- https://git.kernel.org/stable/c/ff05ed4ae214011464a0156f05cac1b0b46b5fbc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52511.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52511
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
