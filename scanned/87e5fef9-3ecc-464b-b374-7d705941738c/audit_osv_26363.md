# [M] usb: typec: ucsi: Don't attempt to resume the ports before they exist

## Summary
Severity: Medium
Advisory: CVE-2023-52938
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52938
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.1 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: ucsi: Don't attempt to resume the ports before they exist

This will fix null pointer dereference that was caused by
the driver attempting to resume ports that were not yet
registered.

## References
- https://git.kernel.org/stable/c/f82060da749c611ed427523b6d1605d87338aac1
- https://git.kernel.org/stable/c/fdd11d7136fd070b3a74d6d8799d9eac28a57fc5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52938.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52938
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
