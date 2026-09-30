# [H] @actions/artifact has an Arbitrary File Write via artifact extraction

## Summary
Severity: High
Advisory: GHSA-6q32-hq47-5qq3
CVE: CVE-2024-42471
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-6q32-hq47-5qq3
Type: github-advisory

## Affected
- npm: `@actions/artifact` — affected >=2.0.0 <2.1.2

## Details
### Impact

Versions of `actions/artifact` before 2.1.7 are vulnerable to arbitrary file write when using `downloadArtifactInternal`, `downloadArtifactPublic`, or `streamExtractExternal` for extracting a specifically crafted artifact that contains path traversal filenames.

### Patches

Upgrade to version 2.1.7 or higher. 

### References

- https://snyk.io/research/zip-slip-vulnerability
- https://github.com/actions/toolkit/pull/1724

### CVE

CVE-2024-42471

### Credits

Justin Taft from Google

## References
- https://github.com/actions/toolkit/security/advisories/GHSA-6q32-hq47-5qq3
- https://nvd.nist.gov/vuln/detail/CVE-2024-42471
- https://github.com/actions/toolkit/pull/1602
- https://github.com/actions/toolkit/pull/1666
- https://github.com/actions/toolkit/pull/1724
- https://github.com/actions/toolkit/commit/29885a805ef3e95a9862dcaa8431c30981960017
- https://github.com/actions/download-artifact/blob/v3/package.json#L31
- https://github.com/actions/toolkit
- https://snyk.io/research/zip-slip-vulnerability
