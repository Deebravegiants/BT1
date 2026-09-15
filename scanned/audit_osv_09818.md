# [H] CVE-2017-11575

## Summary
Severity: High
Advisory: CVE-2017-11575
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11575
Type: osv

## Details
FontForge 20161012 is vulnerable to a buffer over-read in strnmatch (char.c) resulting in DoS or code execution via a crafted otf file, related to a call from the readttfcopyrights function in parsettf.c.

## References
- http://www.debian.org/security/2017/dsa-3958
- https://github.com/fontforge/fontforge/issues/3096
