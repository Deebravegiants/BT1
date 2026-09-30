# [H] USB: serial: io_edgeport: fix use after free in debug printk

## Summary
Severity: High
Advisory: CVE-2024-50267
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50267
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: serial: io_edgeport: fix use after free in debug printk

The "dev_dbg(&urb->dev->dev, ..." which happens after usb_free_urb(urb)
is a use after free of the "urb" pointer.  Store the "dev" pointer at the
start of the function to avoid this issue.

## References
- https://git.kernel.org/stable/c/13d6ff3ca76056d06a9d88300be2a293442ff595
- https://git.kernel.org/stable/c/275258c30bbda29467216e96fb655b16bcc9992b
- https://git.kernel.org/stable/c/314bdf446053e123f37543aa535197ee75f8aa97
- https://git.kernel.org/stable/c/37bb5628379295c1254c113a407cab03a0f4d0b4
- https://git.kernel.org/stable/c/39709ce93f5c3f9eb535efe2afea088805d1128f
- https://git.kernel.org/stable/c/44fff2c16c5aafbdb70c7183dae0a415ae74705e
- https://git.kernel.org/stable/c/e567fc8f7a4460e486e52c9261b1e8b9f5dc42aa
- https://git.kernel.org/stable/c/e6ceb04eeb6115d872d4c4078d12f1170ed755ce
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50267.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50267
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
