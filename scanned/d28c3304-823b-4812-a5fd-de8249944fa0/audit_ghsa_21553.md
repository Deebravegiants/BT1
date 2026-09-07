# [M] Reflected Cross site scripting (XSS) in kairosdb

## Summary
Severity: Medium
Advisory: GHSA-fjhh-67wv-7gr4
CVE: CVE-2019-19040
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-03
Source: https://github.com/advisories/GHSA-fjhh-67wv-7gr4
Type: github-advisory

## Affected
- Maven: `org.kairosdb:kairosdb` — affected >=0 <1.3.0

## Details
KairosDB through 1.2.2 has XSS in view.html because of showErrorMessage in js/graph.js, as demonstrated by view.html?q= with a '"sampling":{"value":"<script>' substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19040
- https://github.com/kairosdb/kairosdb/issues/569
- https://github.com/kairosdb/kairosdb/pull/593
- https://github.com/kairosdb/kairosdb/milestone/10?closed=1
