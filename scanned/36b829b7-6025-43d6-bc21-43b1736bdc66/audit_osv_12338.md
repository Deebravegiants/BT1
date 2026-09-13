# [M] CVE-2018-11383

## Summary
Severity: Medium
Advisory: CVE-2018-11383
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11383
Type: osv

## Details
The r_strbuf_fini() function in radare2 2.5.0 allows remote attackers to cause a denial of service (invalid free and application crash) via a crafted ELF file because of an uninitialized variable in the CPSE handler in libr/anal/p/anal_avr.c.

## References
- https://github.com/radare/radare2/issues/9943
- https://github.com/radare/radare2/commit/9d348bcc2c4bbd3805e7eec97b594be9febbdf9a
