# [C] CVE-2016-2195

## Summary
Severity: Critical
Advisory: CVE-2016-2195
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-2195
Type: osv

## Details
Integer overflow in the PointGFp constructor in Botan before 1.10.11 and 1.11.x before 1.11.27 allows remote attackers to overwrite memory and possibly execute arbitrary code via a crafted ECC point, which triggers a heap-based buffer overflow.

## References
- http://botan.randombit.net/security.html
- http://marc.info/?l=botan-devel&m=145435148602911&w=2
- http://www.debian.org/security/2016/dsa-3565
- https://security.gentoo.org/glsa/201612-38
