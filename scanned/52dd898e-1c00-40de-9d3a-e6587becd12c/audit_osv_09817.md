# [H] CVE-2017-11574

## Summary
Severity: High
Advisory: CVE-2017-11574
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11574
Type: osv

## Details
FontForge 20161012 is vulnerable to a heap-based buffer overflow in readcffset (parsettf.c) resulting in DoS or code execution via a crafted otf file.

## References
- http://www.debian.org/security/2017/dsa-3958
- https://github.com/fontforge/fontforge/issues/3090
