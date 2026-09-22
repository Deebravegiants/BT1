# [H] CVE-2018-5805

## Summary
Severity: High
Advisory: CVE-2018-5805
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5805
Type: osv

## Details
A boundary error within the "quicktake_100_load_raw()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.8 can be exploited to cause a stack-based buffer overflow and subsequently cause a crash.

## References
- https://access.redhat.com/errata/RHSA-2018:3065
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/advisories/81000/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-3/
- https://github.com/LibRaw/LibRaw/commit/9f26ce37f5be86ea11bfc6831366558650b1f6ff
