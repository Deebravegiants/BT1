# [H] ksmbd: add bounds check for durable handle context

## Summary
Severity: High
Advisory: CVE-2025-22043
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22043
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add bounds check for durable handle context

Add missing bounds check for durable handle context.

## References
- https://git.kernel.org/stable/c/1107b9ed92194603593c51829a3887812ae9e806
- https://git.kernel.org/stable/c/29b946714d6aa77de54c71243bba39469ac43ef2
- https://git.kernel.org/stable/c/542027e123fc0bfd61dd59e21ae0ee4ef2101b29
- https://git.kernel.org/stable/c/8d4848c45943c9cf5e86142fd7347efa97f497db
- https://git.kernel.org/stable/c/f0db3d9d416e332a0d6f045a1509539d3a4cd898
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22043.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
