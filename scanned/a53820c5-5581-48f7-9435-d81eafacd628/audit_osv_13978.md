# [M] CVE-2018-5816

## Summary
Severity: Medium
Advisory: CVE-2018-5816
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5816
Type: osv

## Details
An integer overflow error within the "identify()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.12 can be exploited to trigger a division by zero via specially crafted NOKIARAW file (Note: This vulnerability is caused due to an incomplete fix of CVE-2018-5804).

## References
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-14/
- https://usn.ubuntu.com/3838-1/
- https://secuniaresearch.flexerasoftware.com/advisories/83507/
- https://github.com/LibRaw/LibRaw/commit/1d8d1b452e5dc74033ee9f846081a0efb616cc39
