# [M] Cross-site Scripting in apostrophe

## Summary
Severity: Medium
Advisory: GHSA-4r9c-jghc-cx5m
CVE: CVE-2021-25978
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-4r9c-jghc-cx5m
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=2.63.0 <3.4.0

## Details
Apostrophe CMS versions between 2.63.0 to 3.3.1 are vulnerable to Stored XSS where an editor uploads an SVG file that contains malicious JavaScript onto the Images module, which triggers XSS once viewed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25978
- https://github.com/apostrophecms/apostrophe/commit/c8b94ee9c79468f1ce28e31966cb0e0839165e59
- https://github.com/apostrophecms/apostrophe
