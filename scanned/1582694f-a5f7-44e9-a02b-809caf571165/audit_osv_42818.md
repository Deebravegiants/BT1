# [M] Typemill < 2.26.0 Authorization Bypass via Media File Download Route

## Summary
Severity: Medium
Advisory: CVE-2026-71518
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-71518
Type: osv

## Details
Typemill before 2.26.0 contains an authorization bypass vulnerability in the media file download route that allows unauthenticated attackers to access restricted files by submitting path-equivalent URL variants. Attackers can substitute normalized path forms such as dot-slash prefixes, double slashes, or percent-encoded sequences to pass role-based restriction checks while the filesystem resolves the request to the protected file, enabling unauthorized file download without credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71518.json
- https://github.com/typemill/typemill/releases/tag/v2.26.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-71518
- https://www.vulncheck.com/advisories/typemill-authorization-bypass-via-media-file-download-route
- https://github.com/typemill/typemill/commit/8c621063b4697a94342cb0a4b3905adda60e3d25
- https://github.com/typemill/typemill
