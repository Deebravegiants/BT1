# [M] CVE-2019-11190

## Summary
Severity: Medium
Advisory: CVE-2019-11190
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-12
Source: https://osv.dev/vulnerability/CVE-2019-11190
Type: osv

## Details
The Linux kernel before 4.8 allows local users to bypass ASLR on setuid programs (such as /bin/su) because install_exec_creds() is called too late in load_elf_binary() in fs/binfmt_elf.c, and thus the ptrace_may_access() check has a race condition when reading /proc/pid/stat.

## References
- https://usn.ubuntu.com/4008-2/
- https://usn.ubuntu.com/4008-3/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://www.securityfocus.com/bid/107890
- https://lists.debian.org/debian-lts-announce/2019/05/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00042.html
- https://usn.ubuntu.com/4008-1/
- http://www.openwall.com/lists/oss-security/2019/04/15/1
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/stable-queue.git/commit/?id=a5b5352558f6808db0589644ea5401b3e3148a0d
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/stable-queue.git/commit/?id=e1676b55d874a43646e8b2c46d87f2f3e45516ff
- https://www.openwall.com/lists/oss-security/2019/04/03/4
- https://www.openwall.com/lists/oss-security/2019/04/03/4/1
