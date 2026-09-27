# [H] CVE-2018-19503

## Summary
Severity: High
Advisory: CVE-2018-19503
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/CVE-2018-19503
Type: osv

## Details
An issue was discovered in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.1. There was a stack-based buffer overflow in the function calculate_gain() in libfaad/sbr_hfadj.c.

## References
- https://seclists.org/bugtraq/2019/Sep/28
- https://security.gentoo.org/glsa/202006-17
- https://www.debian.org/security/2019/dsa-4522
- https://github.com/TeamSeri0us/pocs/tree/master/faad
- https://sourceforge.net/p/faac/bugs/240/
