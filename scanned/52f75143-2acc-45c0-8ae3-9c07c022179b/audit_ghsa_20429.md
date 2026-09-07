# [M] Open Redirect in node-forge

## Summary
Severity: Medium
Advisory: GHSA-8fr3-hfg3-gpgp
CVE: CVE-2022-0122
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-8fr3-hfg3-gpgp
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.0.0

## Details
parseUrl functionality in node-forge mishandles certain uses of backslash such as `https:/\/\/\` and interprets the URI as a relative path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0122
- https://github.com/digitalbazaar/forge/commit/db8016c805371e72b06d8e2edfe0ace0df934a5e
- https://github.com/digitalbazaar/forge
- https://huntr.dev/bounties/41852c50-3c6d-4703-8c55-4db27164a4ae
