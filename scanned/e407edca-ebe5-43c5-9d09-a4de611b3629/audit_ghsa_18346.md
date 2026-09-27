# [M] github.com/nyaruka/phonenumbers Vulnerable to Improper Validation of Syntactic Correctness of Input

## Summary
Severity: Medium
Advisory: GHSA-fmjh-f678-cv3x
CVE: CVE-2025-10954
CWE: CWE-1286
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-09-27
Source: https://github.com/advisories/GHSA-fmjh-f678-cv3x
Type: github-advisory

## Affected
- Go: `github.com/nyaruka/phonenumbers` — affected >=0 <1.2.2

## Details
Versions of the package github.com/nyaruka/phonenumbers before 1.2.2 are vulnerable to Improper Validation of Syntactic Correctness of Input in the phonenumbers.Parse() function. An attacker can cause a panic by providing crafted input causing a "runtime error: slice bounds out of range".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10954
- https://github.com/nyaruka/phonenumbers/issues/148
- https://github.com/nyaruka/phonenumbers/commit/0479e35488e8a002a261cdb515ef8a7f80ca37fe
- https://github.com/nyaruka/phonenumbers
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMNYARUKAPHONENUMBERS-6084070
