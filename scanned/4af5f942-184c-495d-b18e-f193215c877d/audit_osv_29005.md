# [H] media: i2c: et8ek8: Don't strip remove function when driver is builtin

## Summary
Severity: High
Advisory: CVE-2024-38611
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38611
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.133, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: i2c: et8ek8: Don't strip remove function when driver is builtin

Using __exit for the remove function results in the remove callback
being discarded with CONFIG_VIDEO_ET8EK8=y. When such a device gets
unbound (e.g. using sysfs or hotplug), the driver is just removed
without the cleanup being performed. This results in resource leaks. Fix
it by compiling in the remove callback unconditionally.

This also fixes a W=1 modpost warning:

	WARNING: modpost: drivers/media/i2c/et8ek8/et8ek8: section mismatch in reference: et8ek8_i2c_driver+0x10 (section: .data) -> et8ek8_remove (section: .exit.text)

## References
- https://git.kernel.org/stable/c/04d1086a62ac492ebb6bb0c94c1c8cb55f5d1f36
- https://git.kernel.org/stable/c/43fff07e4b1956d0e5cf23717507e438278ea3d9
- https://git.kernel.org/stable/c/545b215736c5c4b354e182d99c578a472ac9bfce
- https://git.kernel.org/stable/c/904db2ba44ae60641b6378c5013254d09acf5e80
- https://git.kernel.org/stable/c/963523600d9f1e36bc35ba774c2493d6baa4dd8f
- https://git.kernel.org/stable/c/c1a3803e5bb91c13e9ad582003e4288f67f06cd9
- https://git.kernel.org/stable/c/ece3fc1c10197052044048bea4f13cfdcf25b416
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38611.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38611
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
