# [M] Cross-Site Scripting in forms

## Summary
Severity: Medium
Advisory: GHSA-vwjj-2852-3765
CVE: CVE-2017-16015
CWE: CWE-80
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-vwjj-2852-3765
Type: github-advisory

## Affected
- npm: `forms` — affected >=0 <1.3.0

## Details
Affected versions of `forms` do not properly escape HTML in generated forms, which may result in cross-site scripting.


## Recommendation

Update to version 1.3.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16015
- https://github.com/caolan/forms/commit/bc01e534a0ff863dedb2026a50bd03153bbc6a5d
- https://github.com/advisories/GHSA-vwjj-2852-3765
- https://www.npmjs.com/advisories/158
