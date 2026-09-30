# [H] nilfs2: fix nilfs_empty_dir() misjudgment and long loop on I/O errors

## Summary
Severity: High
Advisory: CVE-2024-39469
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-39469
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix nilfs_empty_dir() misjudgment and long loop on I/O errors

The error handling in nilfs_empty_dir() when a directory folio/page read
fails is incorrect, as in the old ext2 implementation, and if the
folio/page cannot be read or nilfs_check_folio() fails, it will falsely
determine the directory as empty and corrupt the file system.

In addition, since nilfs_empty_dir() does not immediately return on a
failed folio/page read, but continues to loop, this can cause a long loop
with I/O if i_size of the directory's inode is also corrupted, causing the
log writer thread to wait and hang, as reported by syzbot.

Fix these issues by making nilfs_empty_dir() immediately return a false
value (0) if it fails to get a directory folio/page.

## References
- https://git.kernel.org/stable/c/11a2edb70356a2202dcb7c9c189c8356ab4752cd
- https://git.kernel.org/stable/c/129dcd3e7d036218db3f59c82d82004b9539ed82
- https://git.kernel.org/stable/c/2ac8a2fe22bdde9eecce2a42cf5cab79333fb428
- https://git.kernel.org/stable/c/405b71f1251e5ae865f53bd27c45114e6c83bee3
- https://git.kernel.org/stable/c/59f14875a96ef93f05b82ad3c980605f2cb444b5
- https://git.kernel.org/stable/c/7373a51e7998b508af7136530f3a997b286ce81c
- https://git.kernel.org/stable/c/c77ad608df6c091fe64ecb91f41ef7cb465587f1
- https://git.kernel.org/stable/c/d18b05eda7fa77f02114f15b02c009f28ee42346
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39469.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39469
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
