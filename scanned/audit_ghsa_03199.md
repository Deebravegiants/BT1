# [C] Prototype Pollution in phpjs

## Summary
Severity: Critical
Advisory: GHSA-m428-jqc4-2p5j
CVE: CVE-2020-7700
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-m428-jqc4-2p5j
Type: github-advisory

## Affected
- npm: `phpjs` — affected >=0

## Details
All versions of phpjs up to and including 1.3.2 are vulnerable to Prototype Pollution via parse_str. phpjs is no longer maintained and users are advised to use Locutus as a replacement (https://github.com/locutusjs/locutus)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7700
- https://snyk.io/vuln/SNYK-JS-PHPJS-598681
