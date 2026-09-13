# [M] CVE-2016-10255

## Summary
Severity: Medium
Advisory: CVE-2016-10255
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-10255
Type: osv

## Details
The __libelf_set_rawdata_wrlock function in elf_getdata.c in elfutils before 0.168 allows remote attackers to cause a denial of service (crash) via a crafted (1) sh_off or (2) sh_size ELF header value, which triggers a memory allocation failure.

## References
- https://lists.fedorahosted.org/archives/list/elfutils-devel%40lists.fedorahosted.org/thread/Q4LE47FPEVRZANMV6JE2NMHYO4H5MHGJ/
- https://usn.ubuntu.com/3670-1/
- http://www.openwall.com/lists/oss-security/2017/03/22/1
- https://blogs.gentoo.org/ago/2016/11/04/elfutils-memory-allocation-failure-in-__libelf_set_rawdata_wrlock-elf_getdata-c/
- https://security.gentoo.org/glsa/201710-10
- https://bugzilla.redhat.com/show_bug.cgi?id=1387584
