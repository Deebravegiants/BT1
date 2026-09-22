# [H] CVE-2017-7578

## Summary
Severity: High
Advisory: CVE-2017-7578
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-07
Source: https://osv.dev/vulnerability/CVE-2017-7578
Type: osv

## Details
Multiple heap-based buffer overflows in parser.c in libming 0.4.7 allow remote attackers to cause a denial of service (listswf application crash) or possibly have unspecified other impact via a crafted SWF file. NOTE: this issue exists because of an incomplete fix for CVE-2016-9831.

## References
- https://github.com/libming/libming/issues/68
