# [M] Sanitizer bypass in svg-sanitizer

## Summary
Severity: Medium
Advisory: GHSA-8rc5-hx3v-2jg7
CVE: CVE-2019-10772
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-02-27
Source: https://github.com/advisories/GHSA-8rc5-hx3v-2jg7
Type: github-advisory

## Affected
- Packagist: `enshrined/svg-sanitize` — affected >=0 <0.13.1

## Details
It is possible to bypass enshrined/svg-sanitize before 0.13.1 using the "xlink:href" attribute due to mishandling of the xlink namespace by the sanitizer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10772
- https://github.com/darylldoyle/svg-sanitizer/commit/6add43e5c5649bc40e3afcb68c522720dcb336f9
- https://snyk.io/vuln/SNYK-PHP-ENSHRINEDSVGSANITIZE-536969
