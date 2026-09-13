# [H] leds: trigger: Unregister sysfs attributes before calling deactivate()

## Summary
Severity: High
Advisory: CVE-2024-43830
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43830
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

leds: trigger: Unregister sysfs attributes before calling deactivate()

Triggers which have trigger specific sysfs attributes typically store
related data in trigger-data allocated by the activate() callback and
freed by the deactivate() callback.

Calling device_remove_groups() after calling deactivate() leaves a window
where the sysfs attributes show/store functions could be called after
deactivation and then operate on the just freed trigger-data.

Move the device_remove_groups() call to before deactivate() to close
this race window.

This also makes the deactivation path properly do things in reverse order
of the activation path which calls the activate() callback before calling
device_add_groups().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0788a6f3523d3686a9eed5ea1e6fcce6841277b2
- https://git.kernel.org/stable/c/09c1583f0e10c918855d6e7540a79461a353e5d6
- https://git.kernel.org/stable/c/3fb6a9d67cfd812a547ac73ec02e1077c26c640d
- https://git.kernel.org/stable/c/734ba6437e80dfc780e9ee9d95f912392d12b5ea
- https://git.kernel.org/stable/c/c0dc9adf9474ecb7106e60e5472577375aedaed3
- https://git.kernel.org/stable/c/c3b7a650c8717aa89df318364609c86cbc040156
- https://git.kernel.org/stable/c/cb8aa9d2a4c8a15d6a43ccf901ef3d094aa60374
- https://git.kernel.org/stable/c/d1415125b701ef13370e2761f691ec632a5eb93a
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43830.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43830
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
