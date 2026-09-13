# [M] CVE-2019-14444

## Summary
Severity: Medium
Advisory: CVE-2019-14444
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-14444
Type: osv

## Details
apply_relocations in readelf.c in GNU Binutils 2.32 contains an integer overflow that allows attackers to trigger a write access violation (in byte_put_little_endian function in elfcomm.c) via an ELF file, as demonstrated by readelf.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00004.html
- https://security.gentoo.org/glsa/202007-39
- https://security.netapp.com/advisory/ntap-20190822-0002/
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=24829
