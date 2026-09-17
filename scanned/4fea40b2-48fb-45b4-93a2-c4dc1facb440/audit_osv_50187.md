# [H] CVE-2019-8980

## Summary
Severity: High
Advisory: CVE-2019-8980
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-21
Source: https://osv.dev/vulnerability/CVE-2019-8980
Type: osv

## Details
A memory leak in the kernel_read_file function in fs/exec.c in the Linux kernel through 4.20.11 allows attackers to cause a denial of service (memory consumption) by triggering vfs_read failures.

## References
- https://www.mail-archive.com/linux-kernel%40vger.kernel.org/msg1935698.html
- https://www.mail-archive.com/linux-kernel%40vger.kernel.org/msg1935705.html
- https://usn.ubuntu.com/3930-2/
- https://usn.ubuntu.com/3931-1/
- https://support.f5.com/csp/article/K56480726
- https://usn.ubuntu.com/3931-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00052.html
- http://www.securityfocus.com/bid/107120
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- https://usn.ubuntu.com/3930-1/
