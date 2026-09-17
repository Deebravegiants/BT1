# [M] can: etas_es58x: fix potential NULL pointer dereference on udev->serial

## Summary
Severity: Medium
Advisory: CVE-2025-21773
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21773
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: etas_es58x: fix potential NULL pointer dereference on udev->serial

The driver assumed that es58x_dev->udev->serial could never be NULL.
While this is true on commercially available devices, an attacker
could spoof the device identity providing a NULL USB serial number.
That would trigger a NULL pointer dereference.

Add a check on es58x_dev->udev->serial before accessing it.

## References
- https://git.kernel.org/stable/c/1590667a60753ee5a54871f2840ceefd4a7831fa
- https://git.kernel.org/stable/c/5059ea98d7bc133903d3e47ab36df6ed11d0c95f
- https://git.kernel.org/stable/c/722e8e1219c8b6ac2865011fe339315d6a8d0721
- https://git.kernel.org/stable/c/a1ad2109ce41c9e3912dadd07ad8a9c640064ffb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21773.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21773
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
