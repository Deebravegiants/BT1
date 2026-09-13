# [M] CVE-2017-11683

## Summary
Severity: Medium
Advisory: CVE-2017-11683
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/CVE-2017-11683
Type: osv

## Details
There is a reachable assertion in the Internal::TiffReader::visitDirectory function in tiffvisitor.cpp of Exiv2 0.26 that will lead to a remote denial of service attack via crafted input.

## References
- http://www.securityfocus.com/bid/100030
- https://lists.debian.org/debian-lts-announce/2022/11/msg00013.html
- https://usn.ubuntu.com/3852-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1475124
