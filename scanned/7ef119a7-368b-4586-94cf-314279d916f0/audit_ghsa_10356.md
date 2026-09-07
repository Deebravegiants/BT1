# [M] AIOHTTP affected by UNC SSRF/NTLMv2 Credential Theft/Local File Read in static resource handler on Windows

## Summary
Severity: Medium
Advisory: GHSA-p998-jp59-783m
CVE: CVE-2026-34515
CWE: CWE-36, CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-p998-jp59-783m
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.4

## Details
### Summary

On Windows the static resource handler may expose information about a NTLMv2 remote path.

### Impact

If an application is running on Windows, and using aiohttp's static resource handler (not recommended in production), then it may be possible for an attacker to extract the hash from an NTLMv2 path and then extract the user's credentials from there.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/0ae2aa076c84573df83fc1fdc39eec0f5862fe3d

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-p998-jp59-783m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34515
- https://github.com/aio-libs/aiohttp/commit/0ae2aa076c84573df83fc1fdc39eec0f5862fe3d
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/releases/tag/v3.13.4
