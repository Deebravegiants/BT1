# [M] Logging of the firestore key within nodejs-firestore

## Summary
Severity: Medium
Advisory: GHSA-4g6q-77j7-vvjc
CVE: CVE-2023-6460
CWE: CWE-532, CWE-922
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-04
Source: https://github.com/advisories/GHSA-4g6q-77j7-vvjc
Type: github-advisory

## Affected
- npm: `@google-cloud/firestore` — affected >=0 <6.1.0

## Details
A potential logging of the firestore key via logging within nodejs-firestore exists - Developers who were logging objects through this._settings would be logging the firestore key as well potentially exposing it to anyone with logs read access. We recommend upgrading to version 6.1.0 to avoid this issue

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6460
- https://github.com/googleapis/nodejs-firestore/pull/1742
- https://bughunters.google.com/reports/vrp/KNvgo1Wij
- https://github.com/googleapis/nodejs-firestore
- https://github.com/googleapis/nodejs-firestore/releases/tag/v6.1.0
