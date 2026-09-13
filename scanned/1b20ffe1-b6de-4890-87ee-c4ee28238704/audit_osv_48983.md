# [H] CVE-2018-19566

## Summary
Severity: High
Advisory: CVE-2018-19566
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-11-26
Source: https://osv.dev/vulnerability/CVE-2018-19566
Type: osv

## Details
A heap buffer over-read in parse_tiff_ifd in dcraw through 9.28 could be used by attackers able to supply malicious files to crash an application that bundles the dcraw code or leak private information.

## References
- https://seclists.org/oss-sec/2018/q4/165
- https://seclists.org/oss-sec/2018/q4/171
