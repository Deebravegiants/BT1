# [H] CVE-2017-13135

## Summary
Severity: High
Advisory: CVE-2017-13135
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-16
Source: https://osv.dev/vulnerability/CVE-2017-13135
Type: osv

## Details
A NULL Pointer Dereference exists in VideoLAN x265, as used in libbpg 0.9.7 and other products, because the CUData::initialize function in common/cudata.cpp mishandles memory-allocation failure.

## References
- http://www.securityfocus.com/bid/101929
- https://github.com/ebel34/bpg-web-encoder/issues/1
