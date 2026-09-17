# [H] Bluetooth: btusb: mediatek: add intf release flow when usb disconnect

## Summary
Severity: High
Advisory: CVE-2024-56757
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-56757
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btusb: mediatek: add intf release flow when usb disconnect

MediaTek claim an special usb intr interface for ISO data transmission.
The interface need to be released before unregistering hci device when
usb disconnect. Removing BT usb dongle without properly releasing the
interface may cause Kernel panic while unregister hci device.

## References
- https://git.kernel.org/stable/c/489304e67087abddc2666c5af0159cb95afdcf59
- https://git.kernel.org/stable/c/cc569d791ab2a0de74f76e470515d25d24c9b84b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56757.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56757
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
