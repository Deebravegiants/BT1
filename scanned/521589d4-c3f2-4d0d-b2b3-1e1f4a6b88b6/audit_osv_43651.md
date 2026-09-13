# [H] Bluetooth: hci_sync: hold conn in hci_connect_big_sync() callback

## Summary
Severity: High
Advisory: CVE-2026-74530
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74530
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: hold conn in hci_connect_big_sync() callback

There is theoretical UAF if the conn is freed while the hci_sync task is
running.

Hold refcount to avoid that. Handle NULL hcon, return 0 + do nothing to
match the previous behavior.

## References
- https://git.kernel.org/stable/c/2d91e6244b69d752503b2d44020d8b0e323dbd38
- https://git.kernel.org/stable/c/56e78b670356caab0b607e8aad4cf819a1909d07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74530.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74530
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
