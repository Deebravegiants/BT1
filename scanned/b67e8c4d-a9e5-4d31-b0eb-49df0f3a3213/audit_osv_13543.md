# [M] CVE-2018-20199

## Summary
Severity: Medium
Advisory: CVE-2018-20199
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-18
Source: https://osv.dev/vulnerability/CVE-2018-20199
Type: osv

## Details
A NULL pointer dereference was discovered in ifilter_bank of libfaad/filtbank.c in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. The vulnerability causes a segmentation fault and application crash, which leads to denial of service because adding to windowed output is mishandled in the ONLY_LONG_SEQUENCE case.

## References
- https://lists.debian.org/debian-lts-announce/2019/08/msg00033.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00020.html
- https://security.gentoo.org/glsa/202006-17
- https://www.debian.org/security/2022/dsa-5109
- https://github.com/knik0/faad2/issues/24
