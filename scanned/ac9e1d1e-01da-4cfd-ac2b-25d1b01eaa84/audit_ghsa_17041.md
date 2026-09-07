# [M] RSSHub Cross-site Scripting vulnerability caused by internal media proxy

## Summary
Severity: Medium
Advisory: GHSA-2wqw-hr4f-xrhh
CVE: CVE-2024-27926
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-2wqw-hr4f-xrhh
Type: github-advisory

## Affected
- npm: `rsshub` — affected >=1.0.0-master.cbbd829 <1.0.0-master.d8ca915

## Details
## Impact
When the specially crafted image is supplied to the internal media proxy, it proxies the image without handling XSS vulnerabilities, allowing for the execution of arbitrary JavaScript code.

Users who access the deliberately constructed URL are affected.

## Patches

This vulnerability was fixed in version https://github.com/DIYgod/RSSHub/commit/4d3e5d79c1c17837e931b4cd253d2013b487aa87. Please upgrade to this or a later version.

## Workarounds

No.

## References
- https://github.com/DIYgod/RSSHub/security/advisories/GHSA-2wqw-hr4f-xrhh
- https://nvd.nist.gov/vuln/detail/CVE-2024-27926
- https://github.com/DIYgod/RSSHub/commit/4d3e5d79c1c17837e931b4cd253d2013b487aa87
- https://github.com/DIYgod/RSSHub
