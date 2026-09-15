# [C] Nuclide Improper Input Validation

## Summary
Severity: Critical
Advisory: GHSA-r83x-wj75-v89r
CVE: CVE-2018-6333
CWE: CWE-20, CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r83x-wj75-v89r
Type: github-advisory

## Affected
- npm: `nuclide` — affected >=0 <0.290.0

## Details
The hhvm-attach deep link handler in Nuclide did not properly sanitize the provided hostname parameter when rendering. As a result, a malicious URL could be used to render HTML and other content inside of the editor's context, which could potentially be chained to lead to code execution. This issue affected Nuclide prior to v0.290.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6333
- https://github.com/facebook/nuclide/commit/65f6bbd683404be1bb569b8d1be84b5d4c74a324
