# [M] vantage6's CORS settings overly permissive

## Summary
Severity: Medium
Advisory: GHSA-4946-85pr-fvxh
CVE: CVE-2024-23823
CWE: CWE-863, CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-4946-85pr-fvxh
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <4.3.0

## Details
### Impact
The vantage6 server has no restrictions on CORS settings. It should be possible for people to set the allowed origins of the server. 

The impact is limited because v6 does not use session cookies

### Patches
No

### Workarounds
No

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-4946-85pr-fvxh
- https://nvd.nist.gov/vuln/detail/CVE-2024-23823
- https://github.com/vantage6/vantage6/commit/70bb4e1d889230a841eb364d6c03accd7dd01a41
- https://github.com/vantage6/vantage6
