# [M] usb: roles: fix NULL pointer issue when put module's reference

## Summary
Severity: Medium
Advisory: CVE-2024-26747
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26747
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: roles: fix NULL pointer issue when put module's reference

In current design, usb role class driver will get usb_role_switch parent's
module reference after the user get usb_role_switch device and put the
reference after the user put the usb_role_switch device. However, the
parent device of usb_role_switch may be removed before the user put the
usb_role_switch. If so, then, NULL pointer issue will be met when the user
put the parent module's reference.

This will save the module pointer in structure of usb_role_switch. Then,
we don't need to find module by iterating long relations.

## References
- https://git.kernel.org/stable/c/0158216805ca7e498d07de38840d2732166ae5fa
- https://git.kernel.org/stable/c/01f82de440f2ab07c259b7573371e1c42e5565db
- https://git.kernel.org/stable/c/1c9be13846c0b2abc2480602f8ef421360e1ad9e
- https://git.kernel.org/stable/c/4b45829440b1b208948b39cc71f77a37a2536734
- https://git.kernel.org/stable/c/e279bf8e51893e1fe160b3d8126ef2dd00f661e1
- https://git.kernel.org/stable/c/ef982fc41055fcebb361a92288d3225783d12913
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26747.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26747
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
