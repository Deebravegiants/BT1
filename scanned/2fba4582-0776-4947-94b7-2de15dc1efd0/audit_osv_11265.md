# [H] CVE-2017-6952

## Summary
Severity: High
Advisory: CVE-2017-6952
Aliases: GHSA-3v99-hpv7-9hh9, PYSEC-2017-113
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/CVE-2017-6952
Type: osv

## Details
Integer overflow in the cs_winkernel_malloc function in winkernel_mm.c in Capstone 3.0.4 and earlier allows attackers to cause a denial of service (heap-based buffer overflow in a kernel driver) or possibly have unspecified other impact via a large value.

## References
- http://www.securityfocus.com/bid/97323
- https://github.com/aquynh/capstone/commit/6fe86eef621b9849f51a5e1e5d73258a93440403
