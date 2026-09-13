# [C] CVE-2017-6886

## Summary
Severity: Critical
Advisory: CVE-2017-6886
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-16
Source: https://osv.dev/vulnerability/CVE-2017-6886
Type: osv

## Details
An error within the "parse_tiff_ifd()" function (internal/dcraw_common.cpp) in LibRaw versions before 0.18.2 can be exploited to corrupt memory.

## References
- http://www.debian.org/security/2017/dsa-3950
- http://www.securityfocus.com/bid/98605
- https://secuniaresearch.flexerasoftware.com/advisories/75737/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-5/
- https://github.com/LibRaw/LibRaw/commit/d7c3d2cb460be10a3ea7b32e9443a83c243b2251
