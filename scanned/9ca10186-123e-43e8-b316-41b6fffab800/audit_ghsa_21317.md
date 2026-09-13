# [H] parse-server crashes when receiving file download request with invalid byte range

## Summary
Severity: High
Advisory: GHSA-h423-w6qv-2wj3
CVE: CVE-2022-39313
CWE: CWE-1284, CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-h423-w6qv-2wj3
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.17
- npm: `parse-server` — affected >=5.0.0 <5.2.8

## Details
### Impact

Parse Server crashes when a file download request is received with an invalid byte range.

### Patches

Improved parsing of the range parameter to properly handle invalid range requests.

### Workarounds

None

### References

- [GHSA-h423-w6qv-2wj3](https://github.com/parse-community/parse-server/security/advisories/GHSA-h423-w6qv-2wj3)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-h423-w6qv-2wj3
- https://nvd.nist.gov/vuln/detail/CVE-2022-39313
- https://github.com/parse-community/parse-server/commit/066f29673ab4030b6b5b90c0c0326f7d3fe7612a
- https://github.com/parse-community/parse-server/commit/3d7a61ecd5231638f01ff1a965b6313043c594a7
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/4.10.17
