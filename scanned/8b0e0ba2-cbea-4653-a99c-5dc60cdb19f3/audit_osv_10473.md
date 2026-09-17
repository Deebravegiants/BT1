# [H] CVE-2017-15932

## Summary
Severity: High
Advisory: CVE-2017-15932
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/CVE-2017-15932
Type: osv

## Details
In radare2 2.0.1, an integer exception (negative number leading to an invalid memory access) exists in store_versioninfo_gnu_verdef() in libr/bin/format/elf/elf.c via crafted ELF files when parsing the ELF version on 32bit systems.

## References
- http://www.securityfocus.com/bid/101614
- https://github.com/radare/radare2/commit/44ded3ff35b8264f54b5a900cab32ec489d9e5b9
- https://github.com/radare/radare2/issues/8743
