# [H] firmware: arm_ffa: Validate framework notification message layout

## Summary
Severity: High
Advisory: CVE-2026-64081
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64081
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_ffa: Validate framework notification message layout

Framework notifications carry an indirect message in the shared RX
buffer. Validate the reported offset and size before using them, reject
zero-length payloads, and ensure that any non-header payload starts at
the UUID field rather than in the middle of the message header.

Use the validated offset and size values for both kmemdup() and the UUID
parsing path so malformed firmware data cannot drive an out-of-bounds
read or an oversized allocation.

## References
- https://git.kernel.org/stable/c/3c51d99449dc5a01c08a7fce6071d6721f5aac83
- https://git.kernel.org/stable/c/4a1cc9e96b311d2609a6f963a5e35bd4ae730d97
- https://git.kernel.org/stable/c/76eb90e2b03de147e12ab68ea8afd8ea0342df0a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64081.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
