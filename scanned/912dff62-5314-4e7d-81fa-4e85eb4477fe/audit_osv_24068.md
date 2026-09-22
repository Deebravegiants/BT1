# [H] HID: nintendo: fix rumble worker null pointer deref

## Summary
Severity: High
Advisory: CVE-2022-49974
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49974
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: nintendo: fix rumble worker null pointer deref

We can dereference a null pointer trying to queue work to a destroyed
workqueue.

If the device is disconnected, nintendo_hid_remove is called, in which
the rumble_queue is destroyed. Avoid using that queue to defer rumble
work once the controller state is set to JOYCON_CTLR_STATE_REMOVED.

This eliminates the null pointer dereference.

## References
- https://git.kernel.org/stable/c/1ff89e06c2e5fab30274e4b02360d4241d6e605e
- https://git.kernel.org/stable/c/7c6e6c334154be16740b44dcd7638fb510b9bd91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49974.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
