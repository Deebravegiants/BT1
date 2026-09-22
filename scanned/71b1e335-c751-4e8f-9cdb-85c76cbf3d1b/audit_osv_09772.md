# [M] CVE-2017-11446

## Summary
Severity: Medium
Advisory: CVE-2017-11446
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-19
Source: https://osv.dev/vulnerability/CVE-2017-11446
Type: osv

## Details
The ReadPESImage function in coders\pes.c in ImageMagick 7.0.6-1 has an infinite loop vulnerability that can cause CPU exhaustion via a crafted PES file.

## References
- http://www.securityfocus.com/bid/99964
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://www.debian.org/security/2017/dsa-4019
- https://github.com/ImageMagick/ImageMagick/issues/537
