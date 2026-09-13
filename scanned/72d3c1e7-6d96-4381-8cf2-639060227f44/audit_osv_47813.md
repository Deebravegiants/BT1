# [C] CVE-2017-12940

## Summary
Severity: Critical
Advisory: CVE-2017-12940
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12940
Type: osv

## Details
libunrar.a in UnRAR before 5.5.7 has an out-of-bounds read in the EncodeFileName::Decode call within the Archive::ReadHeader15 function.

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10241
- https://security.gentoo.org/glsa/201709-24
- http://seclists.org/oss-sec/2017/q3/290
