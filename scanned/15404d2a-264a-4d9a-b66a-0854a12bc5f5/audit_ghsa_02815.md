# [M] Cross Site Scripting in Microweber

## Summary
Severity: Medium
Advisory: GHSA-w7x8-cq7r-g5g9
CVE: CVE-2021-33988
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-10-25
Source: https://github.com/advisories/GHSA-w7x8-cq7r-g5g9
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.2.8

## Details
Cross Site Scripting (XSS). vulnerability exists in Microweber CMS 1.2.7 via the Login form, which could let a malicious user execute Javascript by Inserting code in the request form.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33988
- https://github.com/nck0099/osTicket/issues/2
- https://github.com/microweber/microweber
