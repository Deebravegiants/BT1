# [M] nope-validator Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3phv-83cj-p8p7
CVE: CVE-2020-26309
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/U:Green (CVSS_V4)
Published: 2024-10-26
Source: https://github.com/advisories/GHSA-3phv-83cj-p8p7
Type: github-advisory

## Affected
- npm: `nope-validator` — affected >=0 <0.12.1

## Details
Nope is a JavaScript validator. Versions 0.11.3 and prior contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS). This vulnerability is fixed in 0.12.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26309
- https://github.com/ftonato/nope-validator/issues/352
- https://github.com/ftonato/nope-validator/commit/4564b7444dcd92769e5c5b80420469c9f18b7a05#diff-9c399c46fa266bcf2be2704fbb369181726959e148e95ab548a32ef9ca9e7d47R1
- https://github.com/ftonato/nope-validator/commit/c8af9f93abe8f4786f8f69d2b0518f8ca3652f44
- https://github.com/ftonato/nope-validator
- https://securitylab.github.com/advisories/GHSL-2020-303-redos-nope-validator
