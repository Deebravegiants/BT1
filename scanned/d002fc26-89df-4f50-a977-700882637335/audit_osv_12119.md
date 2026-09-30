# [M] CVE-2018-10372

## Summary
Severity: Medium
Advisory: CVE-2018-10372
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-25
Source: https://osv.dev/vulnerability/CVE-2018-10372
Type: osv

## Details
process_cu_tu_index in dwarf.c in GNU Binutils 2.30 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted binary file, as demonstrated by readelf.

## References
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/103976
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3032
- https://security.gentoo.org/glsa/201908-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=23064
