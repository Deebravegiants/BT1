# [M] MOOS-IvP through 24.8.1 alog Splitting Path Traversal on Windows

## Summary
Severity: Medium
Advisory: CVE-2026-85456
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85456
Type: osv

## Details
MOOS-IvP through 24.8.1 fails to properly validate variable names extracted from alog files in the SplitHandler, allowing attackers to write files outside the split directory. Attackers can supply crafted alog files with backslash sequences in variable names to escape the output directory and append to arbitrary files on Windows systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85456.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85456
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-alog-splitting-path-traversal-on-windows
- https://github.com/moos-ivp/moos-ivp/commit/6f0619e905b325d6b88f76425673045c6e4f6f94
- https://github.com/moos-ivp/moos-ivp/pull/137
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/lib_logutils/SplitHandler.cpp#L189
