# [M] CVE-2017-16910

## Summary
Severity: Medium
Advisory: CVE-2017-16910
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2017-16910
Type: osv

## Details
An error within the "LibRaw::xtrans_interpolate()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.6 can be exploited to cause an invalid read memory access and subsequently a Denial of Service condition.

## References
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/advisories/76000/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-19/
- https://usn.ubuntu.com/3615-1/
- https://github.com/LibRaw/LibRaw/commit/5563e6ddc3f7cb93d98b491194ceebdee7288d36
