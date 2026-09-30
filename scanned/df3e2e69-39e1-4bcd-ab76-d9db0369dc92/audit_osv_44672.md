# [M] MOOS-IvP through 24.8.1 Out-of-Bounds Read in isBraced, isQuoted and isChevroned

## Summary
Severity: Medium
Advisory: CVE-2026-85444
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85444
Type: osv

## Details
MOOS-IvP through 24.8.1 contains a buffer over-read vulnerability in isQuoted(), isBraced(), and isChevroned() functions that strip whitespace but index using the original string length. Attackers can send NODE_REPORT messages with leading or trailing whitespace to read past buffer bounds and access adjacent memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85444.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85444
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-out-of-bounds-read-in-isbraced-isquoted-and-ischevroned
- https://github.com/moos-ivp/moos-ivp/commit/faff8adfa1a69d68614461f679ebbc1d741c51aa
- https://github.com/moos-ivp/moos-ivp/pull/128
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/lib_mbutil/MBUtils.cpp#L1710
