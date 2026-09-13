# [H] Bluetooth: vhci: Prevent use-after-free by removing debugfs files early

## Summary
Severity: High
Advisory: CVE-2025-39861
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39861
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: vhci: Prevent use-after-free by removing debugfs files early

Move the creation of debugfs files into a dedicated function, and ensure
they are explicitly removed during vhci_release(), before associated
data structures are freed.

Previously, debugfs files such as "force_suspend", "force_wakeup", and
others were created under hdev->debugfs but not removed in
vhci_release(). Since vhci_release() frees the backing vhci_data
structure, any access to these files after release would result in
use-after-free errors.

Although hdev->debugfs is later freed in hci_release_dev(), user can
access files after vhci_data is freed but before hdev->debugfs is
released.

## References
- https://git.kernel.org/stable/c/1503756fffe76d5aea2371a4b8dee20c3577bcfd
- https://git.kernel.org/stable/c/28010791193a4503f054e8d69a950ef815deb539
- https://git.kernel.org/stable/c/7cc08f2f127b9a66f46ea918e34353811a7cb378
- https://git.kernel.org/stable/c/bd75eba88e88d7b896b0c737b02a74a12afc235f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39861.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39861
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
