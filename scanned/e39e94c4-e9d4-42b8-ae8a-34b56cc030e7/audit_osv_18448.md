# [M] CVE-2020-27762

## Summary
Severity: Medium
Advisory: CVE-2020-27762
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-27762
Type: osv

## Details
A flaw was found in ImageMagick in coders/hdr.c. An attacker who submits a crafted file that is processed by ImageMagick could trigger undefined behavior in the form of values outside the range of type `unsigned char`. This would most likely lead to an impact to application availability, but could potentially cause other problems related to undefined behavior. This flaw affects ImageMagick versions prior to ImageMagick 7.0.8-68.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1894680
