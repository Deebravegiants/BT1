# [H] nilfs2: fix missing cleanup on rollforward recovery error

## Summary
Severity: High
Advisory: CVE-2024-46781
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46781
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix missing cleanup on rollforward recovery error

In an error injection test of a routine for mount-time recovery, KASAN
found a use-after-free bug.

It turned out that if data recovery was performed using partial logs
created by dsync writes, but an error occurred before starting the log
writer to create a recovered checkpoint, the inodes whose data had been
recovered were left in the ns_dirty_files list of the nilfs object and
were not freed.

Fix this issue by cleaning up inodes that have read the recovery data if
the recovery routine fails midway before the log writer starts.

## References
- https://git.kernel.org/stable/c/07e4dc2fe000ab008bcfe90be4324ef56b5b4355
- https://git.kernel.org/stable/c/1cf1f7e8cd47244fa947d357ef1f642d91e219a3
- https://git.kernel.org/stable/c/35a9a7a7d94662146396199b0cfd95f9517cdd14
- https://git.kernel.org/stable/c/5787fcaab9eb5930f5378d6a1dd03d916d146622
- https://git.kernel.org/stable/c/8e2d1e9d93c4ec51354229361ac3373058529ec4
- https://git.kernel.org/stable/c/9d8c3a585d564d776ee60d4aabec59b404be7403
- https://git.kernel.org/stable/c/ca92c4bff2833cb30d493b935168d6cccd5c805d
- https://git.kernel.org/stable/c/da02f9eb333333b2e4f25d2a14967cff785ac82e
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46781.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46781
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
