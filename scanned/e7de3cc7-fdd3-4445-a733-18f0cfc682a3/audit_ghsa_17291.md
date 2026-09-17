# [M] MJML allows mj-include directory traversal due to an incomplete fix for CVE-2020-12827

## Summary
Severity: Medium
Advisory: GHSA-45h5-66jx-r2wf
CVE: CVE-2025-67898
CWE: CWE-36
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-45h5-66jx-r2wf
Type: github-advisory

## Affected
- npm: `mjml` — affected >=0 <5.0.0-alpha.9

## Details
MJML before 5.0.0-alpha.9 allows mj-include directory traversal to test file existence and (in the type="css" case) read files. NOTE: this issue exists because of an incomplete fix for CVE-2020-12827.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12827
- https://nvd.nist.gov/vuln/detail/CVE-2025-67898
- https://github.com/mjmlio/mjml/issues/3018
- https://github.com/mjmlio/mjml/pull/3033
- https://github.com/mjmlio/mjml/commit/517b376b068e71c713ec4bb4ef9e5b0b7235b8ce
- https://github.com/mjmlio/mjml
