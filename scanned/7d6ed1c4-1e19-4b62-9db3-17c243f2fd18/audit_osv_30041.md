# [H] f2fs: fix to check atomic_file in f2fs ioctl interfaces

## Summary
Severity: High
Advisory: CVE-2024-49859
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49859
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to check atomic_file in f2fs ioctl interfaces

Some f2fs ioctl interfaces like f2fs_ioc_set_pin_file(),
f2fs_move_file_range(), and f2fs_defragment_range() missed to
check atomic_write status, which may cause potential race issue,
fix it.

## References
- https://git.kernel.org/stable/c/10569b682ebe9c75ef06ddd322ae844e9be6374b
- https://git.kernel.org/stable/c/26b07bd2e1f124b0e430c8d250023f7205c549c3
- https://git.kernel.org/stable/c/7cb51731f24b216b0b87942f519f2c67a17107ee
- https://git.kernel.org/stable/c/bfe5c02654261bfb8bd9cb174a67f3279ea99e58
- https://git.kernel.org/stable/c/d6f08c88047accc6127dddb6798a3ff11321539d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49859.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49859
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
