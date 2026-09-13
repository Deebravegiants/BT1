# [C] Prototype Pollution in locutus

## Summary
Severity: Critical
Advisory: GHSA-f98m-q3hr-p5wq
CVE: CVE-2020-7719
CWE: CWE-1321, CWE-20, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-f98m-q3hr-p5wq
Type: github-advisory

## Affected
- npm: `locutus` — affected >=0 <2.0.12

## Details
All versions of package locutus prior to version 2.0.12 are vulnerable to Prototype Pollution via the php.strings.parse_str function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7719
- https://github.com/kvz/locutus/pull/418
- https://github.com/locutusjs/locutus/commit/0eb16d8541838e80f3c2340a9ef93ded7c97290f
- https://github.com/kvz/locutus
- https://snyk.io/vuln/SNYK-JS-LOCUTUS-598675
