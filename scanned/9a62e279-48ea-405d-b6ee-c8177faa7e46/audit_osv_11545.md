# [H] CVE-2017-8393

## Summary
Severity: High
Advisory: CVE-2017-8393
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8393
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to a global buffer over-read error because of an assumption made by code that runs for objcopy and strip, that SHT_REL/SHR_RELA sections are always named starting with a .rel/.rela prefix. This vulnerability causes programs that conduct an analysis of binary programs using the libbfd library, such as objcopy and strip, to crash.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21412
