# [H] f2fs: fix to wait dio completion

## Summary
Severity: High
Advisory: CVE-2024-47726
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47726
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.70, >=6.7.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to wait dio completion

It should wait all existing dio write IOs before block removal,
otherwise, previous direct write IO may overwrite data in the
block which may be reused by other inode.

## References
- https://git.kernel.org/stable/c/3aa5254d80969cb576601fb9fec7a188cc8dc169
- https://git.kernel.org/stable/c/7be13b73409b553d9d9a6cbb042b4d19e2631cc7
- https://git.kernel.org/stable/c/96cfeb0389530ae32ade8a48ae3ae1ac3b6c009d
- https://git.kernel.org/stable/c/c2a7fc514637f640ff55c3f3e3ed879970814a3f
- https://git.kernel.org/stable/c/e3db757ff9b7101ae68650ac5f6dd5743b68164e
- https://git.kernel.org/stable/c/f81302decd64245bb1bd154ecae0f65a9ee21f04
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47726.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47726
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
