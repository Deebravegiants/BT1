# [M] CVE-2018-20623

## Summary
Severity: Medium
Advisory: CVE-2018-20623
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-20623
Type: osv

## Details
In GNU Binutils 2.31.1, there is a use-after-free in the error function in elfcomm.c when called from the process_archive function in readelf.c via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/106370
- https://support.f5.com/csp/article/K38336243
- https://sourceware.org/bugzilla/show_bug.cgi?id=24049
