# [H] private_address_check contains Incomplete List of Disallowed Inputs

## Summary
Severity: High
Advisory: GHSA-3v3c-r5v2-68ph
CVE: CVE-2017-0909
CWE: CWE-184
Ecosystem: RubyGems
Published: 2017-11-30
Source: https://github.com/advisories/GHSA-3v3c-r5v2-68ph
Type: github-advisory

## Affected
- RubyGems: `private_address_check` — affected >=0 <0.4.1

## Details
The private_address_check ruby gem before 0.4.1 is vulnerable to a bypass due to an incomplete blacklist of common private/local network addresses used to prevent server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0909
- https://github.com/jtdowney/private_address_check/pull/3
- https://hackerone.com/reports/288950
- https://github.com/advisories/GHSA-3v3c-r5v2-68ph
- https://github.com/jtdowney/private_address_check
