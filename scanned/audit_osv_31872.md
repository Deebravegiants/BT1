# [M] usb: renesas_usbhs: Flush the notify_hotplug_work

## Summary
Severity: Medium
Advisory: CVE-2025-21917
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21917
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: renesas_usbhs: Flush the notify_hotplug_work

When performing continuous unbind/bind operations on the USB drivers
available on the Renesas RZ/G2L SoC, a kernel crash with the message
"Unable to handle kernel NULL pointer dereference at virtual address"
may occur. This issue points to the usbhsc_notify_hotplug() function.

Flush the delayed work to avoid its execution when driver resources are
unavailable.

## References
- https://git.kernel.org/stable/c/3248c1f833f924246cb98ce7da4569133c1b2292
- https://git.kernel.org/stable/c/394965f90454d6f00fe11879142b720c6c1a872e
- https://git.kernel.org/stable/c/4ca078084cdd5f32d533311d6a0b63a60dcadd41
- https://git.kernel.org/stable/c/4cd847a7b630a85493d0294ad9542c21aafaa246
- https://git.kernel.org/stable/c/552ca6b87e3778f3dd5b87842f95138162e16c82
- https://git.kernel.org/stable/c/830818c8e70c0364e377f0c243b28061ef7967eb
- https://git.kernel.org/stable/c/d50f5c0cd949593eb9a3d822b34d7b50046a06b7
- https://git.kernel.org/stable/c/e5aac1c9b2974636db7ce796ffa6de88fa08335e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21917.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21917
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
