# [M] CVE-2020-21490

## Summary
Severity: Medium
Advisory: CVE-2020-21490
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-21490
Type: osv

## Details
An issue was discovered in GNU Binutils 2.34. It is a memory leak when process microblaze-dis.c. This one will consume memory on each insn disassembled.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=378fd436405b3051df34ac995b2e03fe1f3d1907
- https://security.netapp.com/advisory/ntap-20230929-0007/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25249
