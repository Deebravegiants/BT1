# [M] CVE-2018-13785

## Summary
Severity: Medium
Advisory: CVE-2018-13785
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-09
Source: https://osv.dev/vulnerability/CVE-2018-13785
Type: osv

## Details
In libpng 1.6.34, a wrong calculation of row_factor in the png_check_chunk_length function (pngrutil.c) may trigger an integer overflow and resultant divide-by-zero while processing a crafted PNG file, leading to a denial of service.

## References
- http://www.securityfocus.com/bid/105599
- http://www.securitytracker.com/id/1041889
- https://access.redhat.com/errata/RHSA-2018:3000
- https://access.redhat.com/errata/RHSA-2018:3001
- https://access.redhat.com/errata/RHSA-2018:3002
- https://access.redhat.com/errata/RHSA-2018:3003
- https://access.redhat.com/errata/RHSA-2018:3007
- https://access.redhat.com/errata/RHSA-2018:3008
- https://access.redhat.com/errata/RHSA-2018:3533
- https://access.redhat.com/errata/RHSA-2018:3534
- https://access.redhat.com/errata/RHSA-2018:3671
- https://access.redhat.com/errata/RHSA-2018:3672
- https://access.redhat.com/errata/RHSA-2018:3779
- https://access.redhat.com/errata/RHSA-2018:3852
- https://security.gentoo.org/glsa/201908-10
- https://security.netapp.com/advisory/ntap-20181018-0001/
- https://sourceforge.net/p/libpng/bugs/278/
- https://usn.ubuntu.com/3712-1/
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- https://github.com/glennrp/libpng/commit/8a05766cb74af05c04c53e6c9d60c13fc4d59bf2
