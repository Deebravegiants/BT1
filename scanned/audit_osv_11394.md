# [M] CVE-2017-7609

## Summary
Severity: Medium
Advisory: CVE-2017-7609
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7609
Type: osv

## Details
elf_compress.c in elfutils 0.168 does not validate the zlib compression factor, which allows remote attackers to cause a denial of service (memory consumption) via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://usn.ubuntu.com/3670-1/
- https://security.gentoo.org/glsa/201710-10
- https://blogs.gentoo.org/ago/2017/04/03/elfutils-memory-allocation-failure-in-__libelf_decompress-elf_compress-c
