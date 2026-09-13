# [H] fs/ntfs3: handle attr_set_size() errors when truncating files

## Summary
Severity: High
Advisory: CVE-2025-71289
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2025-71289
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.145, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: handle attr_set_size() errors when truncating files

If attr_set_size() fails while truncating down, the error is silently
ignored and the inode may be left in an inconsistent state.

## References
- https://git.kernel.org/stable/c/3a718675d6af4992e34ffe86b8f36d471a5afe0e
- https://git.kernel.org/stable/c/576248a34b927e93b2fd3fff7df735ba73ad7d01
- https://git.kernel.org/stable/c/6dfea43d11513b7f2892529de55e8f0855108a2c
- https://git.kernel.org/stable/c/92300ac7ff17cad67ff2f3fbb7003afa326134e0
- https://git.kernel.org/stable/c/d73dcd1520d65a34420761641a36b951b14c8c53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71289.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71289
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
