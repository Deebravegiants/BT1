# [M] CVE-2016-10254

## Summary
Severity: Medium
Advisory: CVE-2016-10254
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-10254
Type: osv

## Details
The allocate_elf function in common.h in elfutils before 0.168 allows remote attackers to cause a denial of service (crash) via a crafted ELF file, which triggers a memory allocation failure.

## References
- https://lists.fedorahosted.org/archives/list/elfutils-devel%40lists.fedorahosted.org/message/EJWVY7TMRDEMWPAPNVU3V4MZYG5HANF2/
- https://usn.ubuntu.com/3670-1/
- http://www.openwall.com/lists/oss-security/2017/03/22/2
- https://blogs.gentoo.org/ago/2016/11/04/elfutils-memory-allocation-failure-in-allocate_elf-common-h/
- https://security.gentoo.org/glsa/201710-10
