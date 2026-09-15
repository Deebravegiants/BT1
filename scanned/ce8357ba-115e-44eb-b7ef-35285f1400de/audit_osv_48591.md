# [H] CVE-2017-9871

## Summary
Severity: High
Advisory: CVE-2017-9871
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/CVE-2017-9871
Type: osv

## Details
The III_i_stereo function in layer3.c in mpglib, as used in libmpgdecoder.a in LAME 3.99.5 and other products, allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted audio file.

## References
- http://www.securityfocus.com/bid/99289
- https://blogs.gentoo.org/ago/2017/06/17/lame-stack-based-buffer-overflow-in-iii_i_stereo-layer3-c/
