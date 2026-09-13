# [H] CVE-2018-20657

## Summary
Severity: High
Advisory: CVE-2018-20657
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/CVE-2018-20657
Type: osv

## Details
The demangle_template function in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.31.1, has a memory leak via a crafted string, leading to a denial of service (memory consumption), as demonstrated by cxxfilt, a related issue to CVE-2018-12698.

## References
- http://www.securityfocus.com/bid/106444
- https://access.redhat.com/errata/RHSA-2019:3352
- https://support.f5.com/csp/article/K62602089
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=88539
