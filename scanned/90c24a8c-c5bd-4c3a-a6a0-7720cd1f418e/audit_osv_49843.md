# [H] CVE-2019-19768

## Summary
Severity: High
Advisory: CVE-2019-19768
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-19768
Type: osv

## Details
In the Linux kernel 5.4.0-rc2, there is a use-after-free (read) in the __blk_add_trace function in kernel/trace/blktrace.c (which is used to fill out a blk_io_trace structure and place it in a per-cpu sub-buffer).

## References
- https://usn.ubuntu.com/4346-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4344-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00039.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://usn.ubuntu.com/4342-1/
- https://usn.ubuntu.com/4345-1/
- https://www.debian.org/security/2020/dsa-4698
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://bugzilla.kernel.org/show_bug.cgi?id=205711
