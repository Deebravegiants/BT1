# [M] Cross-site scripting in Centreon

## Summary
Severity: Medium
Advisory: GHSA-r5mf-q76q-f2xq
CVE: CVE-2021-27676
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-r5mf-q76q-f2xq
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <20.10.7

## Details
Centreon version 20.10.2 is affected by a cross-site scripting (XSS) vulnerability. The dep_description (Dependency Description) and dep_name (Dependency Name) parameters are vulnerable to stored XSS. A user has to log in and go to the Configuration > Notifications > Hosts page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27676
- https://github.com/centreon/centreon/pull/9587
- https://github.com/centreon/centreon/releases/tag/20.10.7
- http://centreon.com
