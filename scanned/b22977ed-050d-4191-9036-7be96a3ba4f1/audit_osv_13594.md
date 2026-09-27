# [M] CVE-2018-20481

## Summary
Severity: Medium
Advisory: CVE-2018-20481
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/CVE-2018-20481
Type: osv

## Details
XRef::getEntry in XRef.cc in Poppler 0.72.0 mishandles unallocated XRef entries, which allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted PDF document, when XRefEntry::setFlag in XRef.h is called from Parser::makeStream in Parser.cc.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00018.html
- http://www.securityfocus.com/bid/106321
- https://access.redhat.com/errata/RHSA-2019:2022
- https://access.redhat.com/errata/RHSA-2019:2713
- https://lists.debian.org/debian-lts-announce/2019/03/msg00008.html
- https://usn.ubuntu.com/3865-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/692
- https://gitlab.freedesktop.org/poppler/poppler/merge_requests/143
