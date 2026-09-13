# [H] CVE-2019-7310

## Summary
Severity: High
Advisory: CVE-2019-7310
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-03
Source: https://osv.dev/vulnerability/CVE-2019-7310
Type: osv

## Details
In Poppler 0.73.0, a heap-based buffer over-read (due to an integer signedness error in the XRef::getEntry function in XRef.cc) allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted PDF document, as demonstrated by pdftocairo.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BI7NLDN2HUEU4ZW3D7XPHOAEGT2CKDRO/
- http://www.securityfocus.com/bid/106829
- https://access.redhat.com/errata/RHSA-2019:2022
- https://access.redhat.com/errata/RHSA-2019:2713
- https://lists.debian.org/debian-lts-announce/2019/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00014.html
- https://usn.ubuntu.com/3886-1/
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=12797
- https://gitlab.freedesktop.org/poppler/poppler/issues/717
