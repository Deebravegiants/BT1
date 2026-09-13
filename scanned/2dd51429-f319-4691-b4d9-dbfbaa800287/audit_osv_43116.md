# [H] usb: host: max3421: Fix shift-out-of-bounds in max3421_hub_control()

## Summary
Severity: High
Advisory: CVE-2026-72483
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72483
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: host: max3421: Fix shift-out-of-bounds in max3421_hub_control()

The `max3421_hub_control()` function handles USB hub class requests
to the virtual root hub. In the `default` branches of both the
`ClearPortFeature` and `SetPortFeature` switch statements, it modifies
`max3421_hcd->port_status` by left shifting 1 by the request's `value`
parameter. However, it does not validate whether this shift will exceed
the width of `port_status`.

So if a malicious userspace task with access to the root hub via
/dev/bus/usb/.../001 issues a USBDEVFS_CONTROL ioctl with `wValue`
greater than or equal to 32, the left shift operation invokes
shift-out-of-bounds undefined behavior. This results in arbitrary
bit corruption of `port_status`, including the normally-immutable
change bits, which can bypass internal state checks and confuse the
hub status.

Fix this by rejecting requests whose `value` exceeds the shift width
before performing the shift.

This issue was found using a KLEE-based symbolic execution tool for
kernel drivers that I'm currently developing.

## References
- https://git.kernel.org/stable/c/00dd025324b56d39d37e57a08f473dab3a660f30
- https://git.kernel.org/stable/c/02d03c61e8a7b016956acb48e8a2512d16d87517
- https://git.kernel.org/stable/c/08b1d4cab0230697bc74c63fc4e40170a7559c54
- https://git.kernel.org/stable/c/3be5f24e8270ba53b3c814d13689bb8644c86237
- https://git.kernel.org/stable/c/4da073d57176d8e1c2bca34febfbc81d2560c1a5
- https://git.kernel.org/stable/c/cff06b03b530ae1fe8a13e93a7848f2130e00fb4
- https://git.kernel.org/stable/c/d512bdefd241b98f4d7bcb5bab5614a86411fad4
- https://git.kernel.org/stable/c/e5fa9d8f40746ec3447335c9642c03410f5fd3af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72483.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72483
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
