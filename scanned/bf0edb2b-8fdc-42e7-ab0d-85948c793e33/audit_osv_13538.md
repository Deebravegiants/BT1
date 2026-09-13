# [H] CVE-2018-20194

## Summary
Severity: High
Advisory: CVE-2018-20194
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-18
Source: https://osv.dev/vulnerability/CVE-2018-20194
Type: osv

## Details
There is a stack-based buffer underflow in the third instance of the calculate_gain function in libfaad/sbr_hfadj.c in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. A crafted input will lead to a denial of service or possibly unspecified other impact because limiting the additional noise energy level is mishandled for the G_max <= G case.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00022.html
- https://seclists.org/bugtraq/2019/Sep/28
- https://security.gentoo.org/glsa/202006-17
- https://www.debian.org/security/2019/dsa-4522
- https://github.com/knik0/faad2/issues/21
