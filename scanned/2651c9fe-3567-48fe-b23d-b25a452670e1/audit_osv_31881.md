# [H] HID: intel-ish-hid: Fix use-after-free issue in ishtp_hid_remove()

## Summary
Severity: High
Advisory: CVE-2025-21928
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21928
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: intel-ish-hid: Fix use-after-free issue in ishtp_hid_remove()

The system can experience a random crash a few minutes after the driver is
removed. This issue occurs due to improper handling of memory freeing in
the ishtp_hid_remove() function.

The function currently frees the `driver_data` directly within the loop
that destroys the HID devices, which can lead to accessing freed memory.
Specifically, `hid_destroy_device()` uses `driver_data` when it calls
`hid_ishtp_set_feature()` to power off the sensor, so freeing
`driver_data` beforehand can result in accessing invalid memory.

This patch resolves the issue by storing the `driver_data` in a temporary
variable before calling `hid_destroy_device()`, and then freeing the
`driver_data` after the device is destroyed.

## References
- https://git.kernel.org/stable/c/01b18a330cda61cc21423a7d1af92cf31ded8f60
- https://git.kernel.org/stable/c/07583a0010696a17fb0942e0b499a62785c5fc9f
- https://git.kernel.org/stable/c/0c1fb475ef999d6c22fc3f963fdf20cb3ed1b03d
- https://git.kernel.org/stable/c/560f4d1299342504a6ab8a47f575b5e6b8345ada
- https://git.kernel.org/stable/c/cf1a6015d2f6b1f0afaa0fd6a0124ff2c7943394
- https://git.kernel.org/stable/c/d3faae7f42181865c799d88c5054176f38ae4625
- https://git.kernel.org/stable/c/dea6a349bcaf243fff95dfd0428a26be6a0fb44e
- https://git.kernel.org/stable/c/eb0695d87a81e7c1f0509b7d8ee7c65fbc26aec9
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21928.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21928
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
