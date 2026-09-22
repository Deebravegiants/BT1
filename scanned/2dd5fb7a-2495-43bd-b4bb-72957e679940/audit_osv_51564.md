# [H] CVE-2021-3347

## Summary
Severity: High
Advisory: CVE-2021-3347
Aliases: A-171705902, ASB-A-171705902
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-29
Source: https://osv.dev/vulnerability/CVE-2021-3347
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.10.11. PI futexes have a kernel stack use-after-free during fault handling, allowing local users to execute code in the kernel, aka CID-34b1a1ce1458.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CXAVDAK4RLAHBHHGEPL73UFXSI6BXQ7Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QOBMXDJABYE76RKNBAWA2E4TSSBX7CSJ/
- http://www.openwall.com/lists/oss-security/2021/01/29/5
- http://www.openwall.com/lists/oss-security/2021/01/29/4
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://www.openwall.com/lists/oss-security/2021/01/29/3
- https://security.netapp.com/advisory/ntap-20210304-0005/
- https://www.debian.org/security/2021/dsa-4843
- https://www.openwall.com/lists/oss-security/2021/01/29/1
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=04b79c55201f02ffd675e1231d731365e335c307
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=2156ac1934166d6deb6cd0f6ffc4c1076ec63697
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=34b1a1ce1458f50ef27c54e28eb9b1947012907a
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6ccc84f917d33312eb2846bd7b567639f585ad6d
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c64396cc36c6e60704ab06c1fb1c4a46179c9120
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c5cade200ab9a2a3be9e7f32a752c8d86b502ec7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=12bb3f7f1b03d5913b3f9d4236a488aa7774dfe9
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f2dac39d93987f7de1e20b3988c8685523247ae2
- http://www.openwall.com/lists/oss-security/2021/02/01/4
