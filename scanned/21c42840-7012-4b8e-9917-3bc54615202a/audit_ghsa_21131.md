# [C] Properties-Reader before v2.2.0 vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-jxvf-m3x5-mxwq
CVE: CVE-2020-28471
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-19
Source: https://github.com/advisories/GHSA-jxvf-m3x5-mxwq
Type: github-advisory

## Affected
- npm: `properties-reader` — affected >=0 <2.2.0

## Details
Properties-Reader prior to version 2.2.0 is vulnerable to prototype pollution. Version 2.2.0 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28471
- https://github.com/steveukx/properties/issues/40
- https://github.com/steveukx/properties/commit/0877cc871db9865f58dd9389ce99e61be05380a5
- https://github.com/steveukx/properties/commit/4e4bc392ecfd0a128f48c1d69f64a0d7194fcaab
- https://github.com/steveukx/properties
- https://security.snyk.io/vuln/SNYK-JS-PROPERTIESREADER-1048968
