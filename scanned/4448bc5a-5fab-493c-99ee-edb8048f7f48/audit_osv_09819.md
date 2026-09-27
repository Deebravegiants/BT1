# [M] CVE-2017-11576

## Summary
Severity: Medium
Advisory: CVE-2017-11576
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11576
Type: osv

## Details
FontForge 20161012 does not ensure a positive size in a weight vector memcpy call in readcfftopdict (parsettf.c) resulting in DoS via a crafted otf file.

## References
- http://www.debian.org/security/2017/dsa-3958
- https://github.com/fontforge/fontforge/issues/3091
