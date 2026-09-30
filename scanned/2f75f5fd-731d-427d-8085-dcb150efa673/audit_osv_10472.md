# [H] CVE-2017-15931

## Summary
Severity: High
Advisory: CVE-2017-15931
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/CVE-2017-15931
Type: osv

## Details
In radare2 2.0.1, an integer exception (negative number leading to an invalid memory access) exists in store_versioninfo_gnu_verneed() in libr/bin/format/elf/elf.c via crafted ELF files on 32bit systems.

## References
- http://www.securityfocus.com/bid/101609
- https://github.com/radare/radare2/commit/c6d0076c924891ad9948a62d89d0bcdaf965f0cd
- https://github.com/radare/radare2/issues/8731
