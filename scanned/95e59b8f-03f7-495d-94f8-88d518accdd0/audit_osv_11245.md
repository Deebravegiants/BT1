# [H] CVE-2017-6887

## Summary
Severity: High
Advisory: CVE-2017-6887
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-16
Source: https://osv.dev/vulnerability/CVE-2017-6887
Type: osv

## Details
A boundary error within the "parse_tiff_ifd()" function (internal/dcraw_common.cpp) in LibRaw versions before 0.18.2 can be exploited to cause a memory corruption via e.g. a specially crafted KDC file with model set to "DSLR-A100" and containing multiple sequences of 0x100 and 0x14A TAGs.

## References
- http://www.debian.org/security/2017/dsa-3950
- http://www.securityfocus.com/bid/98592
- https://secuniaresearch.flexerasoftware.com/advisories/75737/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-6/
- https://github.com/LibRaw/LibRaw/commit/d7c3d2cb460be10a3ea7b32e9443a83c243b2251
