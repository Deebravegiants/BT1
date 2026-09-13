# [C] usb: vhci-hcd: Do not drop references before new references are gained

## Summary
Severity: Critical
Advisory: CVE-2024-43883
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-23
Source: https://osv.dev/vulnerability/CVE-2024-43883
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.105, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: vhci-hcd: Do not drop references before new references are gained

At a few places the driver carries stale pointers
to references that can still be used. Make sure that does not happen.
This strictly speaking closes ZDI-CAN-22273, though there may be
similar races in the driver.

## References
- https://git.kernel.org/stable/c/128e82e41cf7d74a562726c1587d9d2ede1a0a37
- https://git.kernel.org/stable/c/4dacdb9720aaab10b6be121eae55820174d97174
- https://git.kernel.org/stable/c/585e6bc7d0a9bf73a8be3d3fb34e86b90cc61a14
- https://git.kernel.org/stable/c/5a3c473b28ae1c1f7c4dc129e30cb19ae6e96f89
- https://git.kernel.org/stable/c/9c3746ce8d8fcb3a2405644fc0eec7fc5312de80
- https://git.kernel.org/stable/c/afdcfd3d6fcdeca2735ca8d994c5f2d24a368f0a
- https://git.kernel.org/stable/c/c3d0857b7fc2c49f68f89128a5440176089a8f54
- https://git.kernel.org/stable/c/e8c1e606dab8c56cf074b43b98d0805de7322ba2
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43883.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
