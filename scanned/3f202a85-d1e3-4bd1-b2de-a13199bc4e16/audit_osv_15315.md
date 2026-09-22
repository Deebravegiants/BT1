# [H] CVE-2019-15296

## Summary
Severity: High
Advisory: CVE-2019-15296
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-21
Source: https://osv.dev/vulnerability/CVE-2019-15296
Type: osv

## Details
An issue was discovered in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. The faad_resetbits function in libfaad/bits.c is affected by a buffer overflow vulnerability. The number of bits to be read is determined by ld->buffer_size - words*4, cast to uint32. If ld->buffer_size - words*4 is negative, a buffer overflow is later performed via getdword_n(&ld->start[words], ld->bytes_left).

## References
- https://seclists.org/bugtraq/2019/Sep/28
- https://lists.debian.org/debian-lts-announce/2019/08/msg00033.html
- https://security.gentoo.org/glsa/202006-17
- https://www.debian.org/security/2019/dsa-4522
- https://github.com/knik0/faad2/commit/942c3e0aee748ea6fe97cb2c1aa5893225316174
