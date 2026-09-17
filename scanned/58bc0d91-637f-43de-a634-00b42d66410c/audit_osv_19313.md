# [M] CVE-2021-20176

## Summary
Severity: Medium
Advisory: CVE-2021-20176
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-02-06
Source: https://osv.dev/vulnerability/CVE-2021-20176
Type: osv

## Details
A divide-by-zero flaw was found in ImageMagick 6.9.11-57 and 7.0.10-57 in gem.c. This flaw allows an attacker who submits a crafted file that is processed by ImageMagick to trigger undefined behavior through a division by zero. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1916610
