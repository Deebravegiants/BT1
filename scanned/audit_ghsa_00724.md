# [H] Regular expression denial of service in url-regex

## Summary
Severity: High
Advisory: GHSA-v4rh-8p82-6h5w
CVE: CVE-2020-7661
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-06-22
Source: https://github.com/advisories/GHSA-v4rh-8p82-6h5w
Type: github-advisory

## Affected
- npm: `url-regex` — affected >=0

## Details
all versions of url-regex are vulnerable to Regular Expression Denial of Service. An attacker providing a very long string in String.test can cause a Denial of Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7661
- https://github.com/kevva/url-regex/issues/70
- https://github.com/kevva/url-regex
- https://snyk.io/vuln/SNYK-JS-URLREGEX-569472
