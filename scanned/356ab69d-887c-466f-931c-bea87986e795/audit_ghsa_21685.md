# [C] Injection in op-browser

## Summary
Severity: Critical
Advisory: GHSA-3hq6-rmv7-39vh
CVE: CVE-2020-7625
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-3hq6-rmv7-39vh
Type: github-advisory

## Affected
- npm: `op-browser` — affected >=0

## Details
op-browser through 1.0.9 is vulnerable to Command Injection. It allows execution of arbitrary commands via the url function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7625
- https://github.com/hiproxy/open-browser/pull/3
- https://github.com/hiproxy/open-browser/pull/4
- https://github.com/hiproxy/open-browser/blob/master/lib/index.js#L75
- https://snyk.io/vuln/SNYK-JS-OPBROWSER-564259
