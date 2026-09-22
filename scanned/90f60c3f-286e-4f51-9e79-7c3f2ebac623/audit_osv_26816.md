# [H] phy: tegra: xusb: Clear the driver reference in usb-phy dev

## Summary
Severity: High
Advisory: CVE-2023-54083
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54083
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: tegra: xusb: Clear the driver reference in usb-phy dev

For the dual-role port, it will assign the phy dev to usb-phy dev and
use the port dev driver as the dev driver of usb-phy.

When we try to destroy the port dev, it will destroy its dev driver
as well. But we did not remove the reference from usb-phy dev. This
might cause the use-after-free issue in KASAN.

## References
- https://git.kernel.org/stable/c/238edc04ddb9d272b38f5419bcd419ad3b92b91b
- https://git.kernel.org/stable/c/82187460347ad58fd6b06d2883da73c3f2df9631
- https://git.kernel.org/stable/c/b6a107c52073496d2e5d2837915f59fb3103832f
- https://git.kernel.org/stable/c/b84998a407a882991916b1a61d987c400d8a0ce6
- https://git.kernel.org/stable/c/c0c2fcb1325d0d4f3b322b5ee49385f8eca2560d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54083.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54083
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
