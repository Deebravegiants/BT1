# [H] CVE-2020-27766

## Summary
Severity: High
Advisory: CVE-2020-27766
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-04
Source: https://osv.dev/vulnerability/CVE-2020-27766
Type: osv

## Details
A flaw was found in ImageMagick in MagickCore/statistic.c. An attacker who submits a crafted file that is processed by ImageMagick could trigger undefined behavior in the form of values outside the range of type `unsigned long`. This would most likely lead to an impact to application availability, but could potentially cause other problems related to undefined behavior. This flaw affects ImageMagick versions prior to 7.0.8-69.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1894686
