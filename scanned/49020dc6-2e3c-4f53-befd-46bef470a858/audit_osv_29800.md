# [H] nilfs2: protect references to superblock parameters exposed in sysfs

## Summary
Severity: High
Advisory: CVE-2024-46780
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46780
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: protect references to superblock parameters exposed in sysfs

The superblock buffers of nilfs2 can not only be overwritten at runtime
for modifications/repairs, but they are also regularly swapped, replaced
during resizing, and even abandoned when degrading to one side due to
backing device issues.  So, accessing them requires mutual exclusion using
the reader/writer semaphore "nilfs->ns_sem".

Some sysfs attribute show methods read this superblock buffer without the
necessary mutual exclusion, which can cause problems with pointer
dereferencing and memory access, so fix it.

## References
- https://git.kernel.org/stable/c/157c0d94b4c40887329418c70ef4edd1a8d6b4ed
- https://git.kernel.org/stable/c/19cfeba0e4b8eda51484fcf8cf7d150418e1d880
- https://git.kernel.org/stable/c/683408258917541bdb294cd717c210a04381931e
- https://git.kernel.org/stable/c/8c6e43b3d5f109cf9c61bc188fcc8175404e924f
- https://git.kernel.org/stable/c/962562d4c70c5cdeb4e955d63ff2017c4eca1aad
- https://git.kernel.org/stable/c/b14e7260bb691d7f563f61da07d61e3c8b59a614
- https://git.kernel.org/stable/c/b90beafac05931cbfcb6b1bd4f67c1923f47040e
- https://git.kernel.org/stable/c/ba97ba173f9625d5f34a986088979eae8b80d38e
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46780.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46780
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
