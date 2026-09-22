# [H] Input: ims-pcu - only expose sysfs attributes on control interface

## Summary
Severity: High
Advisory: CVE-2026-80596
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80596
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: ims-pcu - only expose sysfs attributes on control interface

When the driver was converted to use the driver core to instantiate device
attributes (via .dev_groups in the usb_driver structure), the attributes
started appearing on all interfaces bound to the driver. Since the ims-pcu
driver manually claims the secondary data interface during probe, the
driver core automatically creates the sysfs attributes for that interface
as well.

However, the driver only supports these attributes on the primary control
interface. Data interfaces lack the necessary descriptors and internal
state to handle these requests, and accessing them can lead to unexpected
behavior or crashes.

Fix this by updating the is_visible() callbacks for both the main and OFN
attribute groups to verify that the interface being accessed is indeed the
control interface.

## References
- https://git.kernel.org/stable/c/001428ea4d2c371107cb984108e266adf99f1f1e
- https://git.kernel.org/stable/c/73e6687be0c1c323a8ec5b733f29440a93e08ff2
- https://git.kernel.org/stable/c/7d5e7c8d48f0aaeb9ec90a9a4f450f3c5e422431
- https://git.kernel.org/stable/c/87e2f89dea078572fb9e13864cec2b1bd8e89b71
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80596.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80596
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
