# [M] CVE-2017-18241

## Summary
Severity: Medium
Advisory: CVE-2017-18241
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-21
Source: https://osv.dev/vulnerability/CVE-2017-18241
Type: osv

## Details
fs/f2fs/segment.c in the Linux kernel before 4.13 allows local users to cause a denial of service (NULL pointer dereference and panic) by using a noflush_merge option that triggers a NULL value for a flush_cmd_control data structure.

## References
- https://usn.ubuntu.com/3910-1/
- https://usn.ubuntu.com/3910-2/
- https://www.debian.org/security/2018/dsa-4187
- https://www.debian.org/security/2018/dsa-4188
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d4fdf8ba0e5808ba9ad6b44337783bd9935e0982
- https://github.com/torvalds/linux/commit/d4fdf8ba0e5808ba9ad6b44337783bd9935e0982
