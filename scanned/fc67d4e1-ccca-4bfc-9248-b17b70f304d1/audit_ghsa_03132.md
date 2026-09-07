# [M] Cross-site Scripting in lightning-server

## Summary
Severity: Medium
Advisory: GHSA-gmch-cm2p-9qw9
CVE: CVE-2020-7747
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-gmch-cm2p-9qw9
Type: github-advisory

## Affected
- npm: `lightning-server` — affected >=0

## Details
This affects all versions of package lightning-server. It is possible to inject malicious JavaScript code as part of a session controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7747
- https://github.com/lightning-viz/lightning/blob/master/app/controllers/session.js%23L230
- https://snyk.io/vuln/SNYK-JS-LIGHTNINGSERVER-1019381
