# [M] CVE-2018-1000667

## Summary
Severity: Medium
Advisory: CVE-2018-1000667
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-1000667
Type: osv

## Details
NASM nasm-2.13.03 nasm- 2.14rc15 version 2.14rc15 and earlier contains a memory corruption (crashed) of nasm when handling a crafted file due to function assemble_file(inname, depend_ptr) at asm/nasm.c:482. vulnerability in function assemble_file(inname, depend_ptr) at asm/nasm.c:482. that can result in aborting/crash nasm program. This attack appear to be exploitable via a specially crafted asm file..

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- https://bugzilla.nasm.us/show_bug.cgi?id=3392507
- https://github.com/cyrillos/nasm/issues/3
