# [H] NFC: nci: uart: Set tty->disc_data only in success path

## Summary
Severity: High
Advisory: CVE-2025-38416
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38416
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: nci: uart: Set tty->disc_data only in success path

Setting tty->disc_data before opening the NCI device means we need to
clean it up on error paths.  This also opens some short window if device
starts sending data, even before NCIUARTSETDRIVER IOCTL succeeded
(broken hardware?).  Close the window by exposing tty->disc_data only on
the success path, when opening of the NCI device and try_module_get()
succeeds.

The code differs in error path in one aspect: tty->disc_data won't be
ever assigned thus NULL-ified.  This however should not be relevant
difference, because of "tty->disc_data=NULL" in nci_uart_tty_open().

## References
- https://git.kernel.org/stable/c/000bfbc6bc334a93fffca8f5aa9583e7b6356cb5
- https://git.kernel.org/stable/c/55c3dbd8389636161090a2b2b6d2d709b9602e9c
- https://git.kernel.org/stable/c/a514fca2b8e95838a3ba600f31a18fa60b76d893
- https://git.kernel.org/stable/c/a8acc7080ad55c5402a1b818b3008998247dda87
- https://git.kernel.org/stable/c/ac6992f72bd8e22679c1e147ac214de6a7093c23
- https://git.kernel.org/stable/c/dc7722619a9c307e9938d735cf4a2210d3d48dcb
- https://git.kernel.org/stable/c/e9799db771b2d574d5bf0dfb3177485e5f40d4d6
- https://git.kernel.org/stable/c/fc27ab48904ceb7e4792f0c400f1ef175edf16fe
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38416.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38416
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
