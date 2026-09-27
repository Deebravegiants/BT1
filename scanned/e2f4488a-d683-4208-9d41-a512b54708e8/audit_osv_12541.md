# [H] CVE-2018-12697

## Summary
Severity: High
Advisory: CVE-2018-12697
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-23
Source: https://osv.dev/vulnerability/CVE-2018-12697
Type: osv

## Details
A NULL pointer dereference (aka SEGV on unknown address 0x000000000000) was discovered in work_stuff_copy_to_from in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.30. This can occur during execution of objdump.

## References
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/104538
- https://access.redhat.com/errata/RHSA-2019:2075
- https://security.gentoo.org/glsa/201908-01
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=85454
- https://sourceware.org/bugzilla/show_bug.cgi?id=23057
- https://bugs.launchpad.net/ubuntu/+source/binutils/+bug/1763102
