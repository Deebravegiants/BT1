# [M] CVE-2019-11366

## Summary
Severity: Medium
Advisory: CVE-2019-11366
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-20
Source: https://osv.dev/vulnerability/CVE-2019-11366
Type: osv

## Details
An issue was discovered in atftpd in atftp 0.7.1. It does not lock the thread_list_mutex mutex before assigning the current thread data structure. As a result, the daemon is vulnerable to a denial of service attack due to a NULL pointer dereference. If thread_data is NULL when assigned to current, and modified by another thread before a certain tftpd_list.c check, there is a crash when dereferencing current->next.

## References
- https://usn.ubuntu.com/4540-1/
- https://lists.debian.org/debian-lts-announce/2019/05/msg00012.html
- https://seclists.org/bugtraq/2019/May/16
- https://www.debian.org/security/2019/dsa-4438
- https://security.gentoo.org/glsa/202003-14
- https://sourceforge.net/p/atftp/code/ci/382f76a90b44f81fec00e2f609a94def4a5d3580/
- https://pulsesecurity.co.nz/advisories/atftpd-multiple-vulnerabilities
