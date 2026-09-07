# [M] Cross-site Scripting (XSS) within joomla/filter class

## Summary
Severity: Medium
Advisory: GHSA-qcv6-h33g-hvrc
CVE: CVE-2022-23800
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-qcv6-h33g-hvrc
Type: github-advisory

## Affected
- Packagist: `joomla/filter` — affected >=0 <1.4.4
- Packagist: `joomla/filter` — affected >=2.0.0 <2.0.1

## Details
An issue was discovered in Joomla! 4.0.0 through 4.1.0. Inadequate content filtering leads to XSS vulnerabilities in various components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23800
- https://developer.joomla.org/security-centre/877-20220308-core-inadequate-content-filtering-within-the-filter-code.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/joomla/filter/CVE-2022-23800.yaml
- https://github.com/joomla-framework/filter
