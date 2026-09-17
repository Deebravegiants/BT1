# [H] firewire: core: fix invalid port index for parent device

## Summary
Severity: High
Advisory: CVE-2024-50113
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50113
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

firewire: core: fix invalid port index for parent device

In a commit 24b7f8e5cd65 ("firewire: core: use helper functions for self
ID sequence"), the enumeration over self ID sequence was refactored with
some helper functions with KUnit tests. These helper functions are
guaranteed to work expectedly by the KUnit tests, however their application
includes a mistake to assign invalid value to the index of port connected
to parent device.

This bug affects the case that any extra node devices which has three or
more ports are connected to 1394 OHCI controller. In the case, the path
to update the tree cache could hits WARN_ON(), and gets general protection
fault due to the access to invalid address computed by the invalid value.

This commit fixes the bug to assign correct port index.

## References
- https://git.kernel.org/stable/c/90753a38bc3d058820981f812a908a99f7b337c1
- https://git.kernel.org/stable/c/f6a6780e0b9bbcf311a727afed06fee533a5e957
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50113.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50113
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
