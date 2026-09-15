# [H] HID: nvidia-shield: Reference hid_device devm allocation of input_dev name

## Summary
Severity: High
Advisory: CVE-2023-53253
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53253
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: nvidia-shield: Reference hid_device devm allocation of input_dev name

Use hid_device for devm allocation of the input_dev name to avoid a
use-after-free. input_unregister_device would trigger devres cleanup of all
resources associated with the input_dev, free-ing the name. The name would
subsequently be used in a uevent fired at the end of unregistering the
input_dev.

## References
- https://git.kernel.org/stable/c/197d3143520fec9fde89aebabc9f0d7464f08e50
- https://git.kernel.org/stable/c/b85d3807e5ec368bfd5b20245347d7c1434aff76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53253.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
