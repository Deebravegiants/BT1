# [H] net: usb: lan78xx: Fix double free issue with interrupt buffer allocation

## Summary
Severity: High
Advisory: CVE-2024-53213
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53213
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.120, >=5.17.0 <6.6.64, >=6.2.0 <6.11.11, >=6.7.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: lan78xx: Fix double free issue with interrupt buffer allocation

In lan78xx_probe(), the buffer `buf` was being freed twice: once
implicitly through `usb_free_urb(dev->urb_intr)` with the
`URB_FREE_BUFFER` flag and again explicitly by `kfree(buf)`. This caused
a double free issue.

To resolve this, reordered `kmalloc()` and `usb_alloc_urb()` calls to
simplify the initialization sequence and removed the redundant
`kfree(buf)`.  Now, `buf` is allocated after `usb_alloc_urb()`, ensuring
it is correctly managed by  `usb_fill_int_urb()` and freed by
`usb_free_urb()` as intended.

## References
- https://git.kernel.org/stable/c/03819abbeb11117dcbba40bfe322b88c0c88a6b6
- https://git.kernel.org/stable/c/2970ef2fce90c661952ec2b451b0276d5f8d6180
- https://git.kernel.org/stable/c/7ac9f3c981eeceee2ec4d30d850f4a6f50a1ec40
- https://git.kernel.org/stable/c/977128343fc2a30737399b58df8ea77e94f164bd
- https://git.kernel.org/stable/c/a422ebec863d99d5607fb41bb7af3347fcb436d3
- https://git.kernel.org/stable/c/b09512aea6223eec756f52aa584fc29eeab57480
- https://git.kernel.org/stable/c/cc5aa8e3ad69dcedeba79e667d4a2efb72a305af
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53213.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53213
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
