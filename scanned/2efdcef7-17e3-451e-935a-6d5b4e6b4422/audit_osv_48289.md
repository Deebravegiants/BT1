# [H] CVE-2017-5669

## Summary
Severity: High
Advisory: CVE-2017-5669
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2017-5669
Type: osv

## Details
The do_shmat function in ipc/shm.c in the Linux kernel through 4.9.12 does not restrict the address calculated by a certain rounding operation, which allows local users to map page zero, and consequently bypass a protection mechanism that exists for the mmap system call, by making crafted shmget and shmat system calls in a privileged context.

## References
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- http://www.debian.org/security/2017/dsa-3804
- http://www.securityfocus.com/bid/96754
- http://www.securitytracker.com/id/1037918
- https://bugzilla.kernel.org/show_bug.cgi?id=192931
- https://github.com/torvalds/linux/commit/95e91b831f87ac8e1f8ed50c14d709089b4e01b8
- https://github.com/torvalds/linux/commit/e1d35d4dc7f089e6c9c080d556feedf9c706f0c7
