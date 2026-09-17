# [M] CVE-2020-27770

## Summary
Severity: Medium
Advisory: CVE-2020-27770
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-04
Source: https://osv.dev/vulnerability/CVE-2020-27770
Type: osv

## Details
Due to a missing check for 0 value of `replace_extent`, it is possible for offset `p` to overflow in SubstituteString(), causing potential impact to application availability. This could be triggered by a crafted input file that is processed by ImageMagick. This flaw affects ImageMagick versions prior to 7.0.8-68.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1894691
