# [H] Bluetooth: RFCOMM: avoid leaving dangling sk pointer in rfcomm_sock_alloc()

## Summary
Severity: High
Advisory: CVE-2024-56604
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56604
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: RFCOMM: avoid leaving dangling sk pointer in rfcomm_sock_alloc()

bt_sock_alloc() attaches allocated sk object to the provided sock object.
If rfcomm_dlc_alloc() fails, we release the sk object, but leave the
dangling pointer in the sock object, which may cause use-after-free.

Fix this by swapping calls to bt_sock_alloc() and rfcomm_dlc_alloc().

## References
- https://git.kernel.org/stable/c/32df687e129ef0f9afcbcc914f7c32deb28fd481
- https://git.kernel.org/stable/c/3945c799f12b8d1f49a3b48369ca494d981ac465
- https://git.kernel.org/stable/c/6021ccc2471b7b95e29b7cfc7938e042bf56e281
- https://git.kernel.org/stable/c/ac3eaac4cf142a15fe67be747a682b1416efeb6e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56604.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56604
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
