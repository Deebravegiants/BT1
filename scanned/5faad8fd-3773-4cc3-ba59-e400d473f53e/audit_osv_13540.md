# [H] CVE-2018-20196

## Summary
Severity: High
Advisory: CVE-2018-20196
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-18
Source: https://osv.dev/vulnerability/CVE-2018-20196
Type: osv

## Details
There is a stack-based buffer overflow in the third instance of the calculate_gain function in libfaad/sbr_hfadj.c in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. A crafted input will lead to a denial of service or possibly unspecified other impact because the S_M array is mishandled.

## References
- https://lists.debian.org/debian-lts-announce/2019/08/msg00033.html
- https://security.gentoo.org/glsa/202006-17
- https://www.debian.org/security/2022/dsa-5109
- https://github.com/knik0/faad2/issues/19
