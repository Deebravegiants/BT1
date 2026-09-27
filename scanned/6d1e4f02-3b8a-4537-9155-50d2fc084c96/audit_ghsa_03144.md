# [M] Improper Input Validation in Google Closure Library

## Summary
Severity: Medium
Advisory: GHSA-vh5w-fg69-rc8m
CVE: CVE-2020-8910
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-vh5w-fg69-rc8m
Type: github-advisory

## Affected
- npm: `google-closure-library` — affected >=0 <20200315.0.0

## Details
A URL parsing issue in goog.uri of the Google Closure Library versions up to and including v20200224 allows an attacker to send malicious URLs to be parsed by the library and return the wrong authority. Mitigation -- update your library to version v20200315.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8910
- https://github.com/google/closure-library/commit/294fc00b01d248419d8f8de37580adf2a0024fc9
- https://github.com/google/closure-library/releases/tag/v20200315
