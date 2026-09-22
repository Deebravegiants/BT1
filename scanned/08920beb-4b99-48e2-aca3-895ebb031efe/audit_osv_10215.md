# [H] CVE-2017-14333

## Summary
Severity: High
Advisory: CVE-2017-14333
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14333
Type: osv

## Details
The process_version_sections function in readelf.c in GNU Binutils 2.29 allows attackers to cause a denial of service (Integer Overflow, and hang because of a time-consuming loop) or possibly have unspecified other impact via a crafted binary file with invalid values of ent.vn_next, during "readelf -a" execution.

## References
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=21990
