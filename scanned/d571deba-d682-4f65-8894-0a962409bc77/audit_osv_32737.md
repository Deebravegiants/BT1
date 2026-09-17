# [H] spi: spi-imx: Add check for spi_imx_setupxfer()

## Summary
Severity: High
Advisory: CVE-2025-37801
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37801
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-imx: Add check for spi_imx_setupxfer()

Add check for the return value of spi_imx_setupxfer().
spi_imx->rx and spi_imx->tx function pointer can be NULL when
spi_imx_setupxfer() return error, and make NULL pointer dereference.

 Unable to handle kernel NULL pointer dereference at virtual address 0000000000000000
 Call trace:
  0x0
  spi_imx_pio_transfer+0x50/0xd8
  spi_imx_transfer_one+0x18c/0x858
  spi_transfer_one_message+0x43c/0x790
  __spi_pump_transfer_message+0x238/0x5d4
  __spi_sync+0x2b0/0x454
  spi_write_then_read+0x11c/0x200

## References
- https://git.kernel.org/stable/c/055ef73bb1afc3f783a9a13b496770a781964a07
- https://git.kernel.org/stable/c/185d376875ea6fb4256b9dc97ee0b4d2b0fdd399
- https://git.kernel.org/stable/c/2b4479eb462ecb39001b38dfb331fc6028dedac8
- https://git.kernel.org/stable/c/2fea0d6d7b5d27fbf55512d51851ba0a346ede52
- https://git.kernel.org/stable/c/951a04ab3a2db4029debfa48d380ef834b93207e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37801.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37801
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
