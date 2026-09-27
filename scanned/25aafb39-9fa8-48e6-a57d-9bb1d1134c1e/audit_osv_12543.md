# [C] CVE-2018-12699

## Summary
Severity: Critical
Advisory: CVE-2018-12699
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-23
Source: https://osv.dev/vulnerability/CVE-2018-12699
Type: osv

## Details
finish_stab in stabs.c in GNU Binutils 2.30 allows attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact, as demonstrated by an out-of-bounds write of 8 bytes. This can occur during execution of objdump.

## References
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/104540
- https://security.gentoo.org/glsa/201908-01
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=85454
- https://sourceware.org/bugzilla/show_bug.cgi?id=23057
- https://bugs.launchpad.net/ubuntu/+source/binutils/+bug/1763102
