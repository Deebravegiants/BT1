# [M] CVE-2018-5812

## Summary
Severity: Medium
Advisory: CVE-2018-5812
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5812
Type: osv

## Details
An error within the "nikon_coolscan_load_raw()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.9 can be exploited to trigger a NULL pointer dereference.

## References
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-10/
- https://usn.ubuntu.com/3838-1/
- https://secuniaresearch.flexerasoftware.com/advisories/81800/
- https://github.com/LibRaw/LibRaw/commit/fd6330292501983ac75fe4162275794b18445bd9
