# [M] Mediawiki - DataTransfer Extension Cross-Site Request Forgery (CSRF) and Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-c3h5-h73c-29hq
CVE: CVE-2025-23081
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-c3h5-h73c-29hq
Type: github-advisory

## Affected
- Packagist: `mediawiki/data-transfer` — affected >=1.39.0 <1.39.11
- Packagist: `mediawiki/data-transfer` — affected >=1.41.0 <1.41.3
- Packagist: `mediawiki/data-transfer` — affected >=1.42.0 <1.42.2

## Details
Cross-Site Request Forgery (CSRF), Improper Neutralization of Input During Web Page Generation (XSS or 'Cross-site Scripting') vulnerability in Wikimedia Foundation Mediawiki - DataTransfer Extension allows Cross Site Request Forgery, Cross-Site Scripting (XSS).This issue affects Mediawiki - DataTransfer Extension: from 1.39.X before 1.39.11, from 1.41.X before 1.41.3, from 1.42.X before 1.42.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-23081
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/DataTransfer/+/1080451
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/DataTransfer/+/1093931
- https://gerrit.wikimedia.org/r/q/I5e1538a3bf66378810f905834c05626e1d2c82f0
- https://gerrit.wikimedia.org/r/q/I773c616db781d2f3f30893ad01ef503bf251a2b3
- https://gerrit.wikimedia.org/r/q/I7c9de4c8dcdb3276ba923c6bc7c8eef3531324c7
- https://gerrit.wikimedia.org/r/q/I9223c31f02f31f1e06e1a8cddf7d539cc8d3a3d9
- https://github.com/wikimedia/mediawiki-extensions-DataTransfer
- https://phabricator.wikimedia.org/T379749
