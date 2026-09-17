# [M] CVE-2021-20241

## Summary
Severity: Medium
Advisory: CVE-2021-20241
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2021-20241
Type: osv

## Details
A flaw was found in ImageMagick in coders/jp2.c. An attacker who submits a crafted file that is processed by ImageMagick could trigger undefined behavior in the form of math division by zero. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1928952
- https://github.com/ImageMagick/ImageMagick/pull/3177
