# [H] sparc: fix accurate exception reporting in copy_{from_to}_user for Niagara

## Summary
Severity: High
Advisory: CVE-2025-40112
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40112
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

sparc: fix accurate exception reporting in copy_{from_to}_user for Niagara

The referenced commit introduced exception handlers on user-space memory
references in copy_from_user and copy_to_user. These handlers return from
the respective function and calculate the remaining bytes left to copy
using the current register contents. This commit fixes a couple of bad
calculations and a broken epilogue in the exception handlers. This will
prevent crashes and ensure correct return values of copy_from_user and
copy_to_user in the faulting case. The behaviour of memcpy stays unchanged.

## References
- https://git.kernel.org/stable/c/05440320ea3e249d5f984918f2bf51210c1a7c03
- https://git.kernel.org/stable/c/088c5098ec6d6b0396edfbf3dad3e81de8469c1c
- https://git.kernel.org/stable/c/0b67c8fc10b13a9090340c5f8a37d308f4e1571c
- https://git.kernel.org/stable/c/37547d8e6eba87507279ee3dfddfd9dc46335454
- https://git.kernel.org/stable/c/7823fc4d8ab5e57f8db7806ff2530c03c166c4bb
- https://git.kernel.org/stable/c/8cdeb5e482d3fdce7e825444b6ca3865e24c0228
- https://git.kernel.org/stable/c/a365ee556e45f780ee322b349a06efdad0c1458f
- https://git.kernel.org/stable/c/a90ce516a73dbe087f9bf3dbf311301a58d125c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40112.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
